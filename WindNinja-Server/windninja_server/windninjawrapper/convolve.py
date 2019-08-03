# The rest of these libraries are mostly for utility functions
import copy
import json
import os
import time

# Numpy is a helpful library because it enables us to use
# vectors and matrices in our calculations
import numpy as np

# Coordinate projection
from osgeo import ogr, osr
from scipy import misc

USE_SCIPY = False
DEBUG = False
SEPARATE_FILES = False

DIR_PATH = os.path.dirname(os.path.realpath(__file__))


################################# CONSTANTS ###########################################
SOURCE_PROJ = osr.SpatialReference()
TARGET_PROJ = osr.SpatialReference()
TARGET_PROJ.ImportFromEPSG(3857)
TRANSFORM = None


# Parse time and data type from file name
def parseFileName(file_path):
    # All file names will be of the format:
    #   20171019T1700_ang.asc
    # With '_' separating the formatted date
    # and the file type.
    # NOTE:
    # The full file path is given so we have
    # to strip the name to just the file name
    file_name = os.path.basename(file_path)
    # This is a much simpler formatting than
    # the previous iteration
    date, file_end = file_name.split("_")
    data_type, extension = file_end.split(".")
    return date, data_type


def dataFromASC(path, data_type):
    with open(path, "r") as f:
        raw_data = f.read().split("\n")  # Break on new line character

    # Create a dictionary to hold all attributes of file data
    data = {}
    # The first 6 lines of each file contain meta data.
    # We iterate over those values and add them to the dictionary.
    # Each of these entries is of the form "key\tvalue".
    for i in range(6):
        k, v = raw_data[i].split("\t")
        data[k] = float(v)

    # Create an 2D array (matrix) of the included data
    mat_data = []
    # NOTE: the headers end at row 6 so we would normally
    # begin at 6 in this range.
    # However, the first row and the last column of
    # these asc files are padding for some other program's
    # input.
    # We don't need that padding (and it would mess up our data)
    # so we don't include these rows.
    # Thus we'll skip the first row of data and begin at 7
    for i in range(7, len(raw_data)):
        # This data is also tab separated.
        # We also include a check for empty values "".
        # This happens if the file has trailing \t
        row = [float(_) for _ in raw_data[i].split("\t") if _ != ""]
        # Make sure there's at least one entry in the row
        if len(row) > 0:
            # A similar explanation of why we're using row[:-1]
            # instead of just row follows from why we're
            # beginning the iteration at 6 instead of 7.
            # The last column of data is padding so
            # we need to clip that element off from all
            # data we add to our matrix.
            if data_type == "ang":
                # NOTE: the ascii output from WindNinja returns angular value of "dir".
                # However we're using the value "AM_dir" in the app.
                # These values differ by 180 degrees so this line
                # is to rectify that.
                vals = [(r + 180) % 360 for r in row[:-1]]
            elif data_type == "vel":
                vals = row[:-1]
            mat_data.append(vals)

    # Convert our list of lists to a numpy array
    data["data"] = np.array(mat_data)
    return data


def coordsFromASC(path):
    with open(path, "r") as f:
        raw_data = f.read().split("\n")  # Break on new line character

    # Create a dictionary to hold all attributes of file data
    data = {}
    # The first 6 lines of each file contain meta data.
    # We iterate over those values and add them to the dictionary.
    # Each of these entries is of the form "key\tvalue".
    for i in range(6):
        k, v = raw_data[i].split("\t")
        data[k] = float(v)

    # Create an array of coordinates from the meta data
    init_x = data["xllcorner"]
    init_y = data["yllcorner"]
    spacer = data["cellsize"]
    x_coords = []
    y_coords = []

    # NOTE: The first row and the last column
    # of the ascii files are padding.
    # We do not read these rows/columns because
    # they are duplicates and it would mess up our data.
    # Hence we skip the first row:
    for i in range(1, int(data["nrows"])):
        x_row = []
        y_row = []
        # And we skip the last column
        for j in range(int(data["ncols"]) - 1):
            x = init_x + (j * spacer) + int(spacer / 2)  # Center the point
            y = init_y + (i * spacer) + int(spacer / 2)  # Center the point
            x_row.append(x)
            y_row.append(y)
        x_coords.append(x_row)
        y_coords.append(y_row)

    # Reverse x because the initial coordinate is lower left corner.
    # Thus we've added the x's going down when they should be going up.
    # A reverse fixes this.
    return (
        np.array(x_coords),
        np.array(y_coords[::-1]),
        int(spacer),
    )  # return resolution as well


# Read all files and add their information
# to one master dictionary
def createTimeDictionary(files, given_max_vel):
    time_dict = {}
    x, y, r = coordsFromASC(files[0])
    # The inclusion of the "data" key here
    # is to make formatting between
    # values uniform
    time_dict["x"] = {"data": x}
    time_dict["y"] = {"data": y}
    # An initially hard-coded value that will later
    # keep track of how many resizes we've performed
    time_dict["resolution"] = {"data": r}
    # Keep track of maximum velocity across all times
    max_vel = 0
    for file_name in files:
        formatted_date, data_type = parseFileName(file_name)
        key = "{}_{}".format(data_type, formatted_date)
        time_dict[key] = dataFromASC(file_name, data_type)
        # Set the maximum velocity
        if data_type == "vel":
            time_max_vel = np.max(time_dict[key]["data"])
            max_vel = max(max_vel, time_max_vel)
    # Maximum velocity can be provided
    # in which case we use that value
    if given_max_vel and given_max_vel > 0:
        print("Using maximum velocity value of {}".format(given_max_vel))
        return time_dict, given_max_vel
    else:
        print(
            "Not given a positive value for maximum velocity ({}), using calculated value of {}".format(
                given_max_vel, max_vel
            )
        )
        return time_dict, max_vel


def resize(mat, use_scipy=False):
    if use_scipy:
        resized = misc.imresize(mat, 0.5, interp="nearest", mode="F")
    else:
        # my own resizing algorithm (replaces scipy.misc.imresize)
        # so we don't have to use scipy
        # which is generally a pain in the ass to install.

        # KERNEL
        # The array by which we convolute over the
        # given matrix.
        kernel = np.array([[0.25, 0.25], [0.25, 0.25]])
        # Get the  height and width of the kernel
        x_len_kernel = kernel.shape[0]
        y_len_kernel = kernel.shape[1]
        # Get the number of times the kernel will fit into
        # our given matrix.
        # This is equivalent to the floor of shape/kernel_length
        max_x = x_len_kernel * (mat.shape[0] // x_len_kernel)
        max_y = y_len_kernel * (mat.shape[1] // y_len_kernel)
        # This array will hold our values
        resized = np.zeros((max_x // x_len_kernel, max_y // y_len_kernel))

        # Iterate over all chunks of the original matrix
        # of size equal to the kernel size.
        # NOTE: This is a skip window.
        # Other convolution techniques would use a sliding window.
        for i in range(0, max_x, x_len_kernel):
            for j in range(0, max_y, y_len_kernel):
                resized[i // x_len_kernel, j // y_len_kernel] = np.vdot(
                    kernel, mat[i : i + x_len_kernel, j : j + y_len_kernel]
                )
    return resized


def resizeAll(time_dict):
    # NOTE: the use of mode="F" is critical to ensure
    # our values don't get converted to integers
    keys = list(time_dict.keys())
    for k in keys:
        # Do not resize resolution data
        if k != "resolution":
            # Special case for angular data
            if "ang" in k:
                # First convert from degrees to radian
                radian_mat = np.deg2rad(time_dict[k]["data"])
                # Next we get the unit vector's x and y components
                unit_x = np.cos(radian_mat)
                unit_y = np.sin(radian_mat)
                # We then apply the resizing operation on the x and y
                # components separately
                resize_x = resize(unit_x, USE_SCIPY)
                resize_y = resize(unit_y, USE_SCIPY)

                # Then we recombine the vector components into an angle (radian)
                resize_rad = np.arctan2(resize_y, resize_x)
                # Conversion back to degrees
                #   NOTE: I'm converting to float32 so it can be passed to imshow for viewing
                deg_mat = np.rad2deg(resize_rad, dtype="float32")
                time_dict[k]["data"] = deg_mat
            else:
                time_dict[k]["data"] = resize(time_dict[k]["data"], USE_SCIPY)
    return time_dict


# Create a dictionary as a lookup for
# changing velocity (raw) values to range indicators.
# In this case we want to divide the velocity into
# 5 buckets (very low, low, regular, high, very high).
# This function creates a dictionary for looking up those values.
def createVelocityRange(max_vel):
    # minimum  velocity is always 0
    NUM_BUCKETS = 5  # this probably won't ever change
    vel_range = {}
    # Populate the range dictionary
    for i in range(NUM_BUCKETS):
        val = i + 1  # the +1 ensures our buckets start at 1 instead of 0
        key = round((max_vel / NUM_BUCKETS) * val, 2)
        vel_range[key] = int(val)
    return vel_range


# This function takes the raw velocity value and
# returns its corresponding bucket.
def vel2Bucket(vel, vel_range):
    # Create our search range
    search_range = list(vel_range.keys()) + [0]  # 0 is always our minimum
    search_range.sort()
    # Iterate over the current (smaller) value and the next (larger)
    for min_vel, max_vel in zip(search_range[:-1], search_range[1:]):
        # If the given velocity value falls between two values return the bucket value
        if min_vel < round(vel, 2) <= max_vel:
            bucket_val = vel_range[max_vel]
        elif vel == 0:  # Special case for minimum value
            bucket_val = 1
        # TODO: catch better
        # elif round(vel,2) > max_vel: # this case should be impossible, but arises through rounding error.
        #    bucket_val = vel_range[max_vel]
    try:
        return bucket_val
    except Exception:
        if vel > max_vel:
            print(
                "Warning: velocity {} greater than maximum velocity of {}.  Assigning maximum value instead".format(
                    vel, max_vel
                )
            )
            return 5


# This function takes an array and applies val2Bucket
# to each entry and returns an array of the same size
def array2Bucket(array, vel_range):
    bucket_array = np.zeros(array.shape)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            bucket_array[i, j] = vel2Bucket(array[i, j], vel_range)
    return bucket_array


# Perform data casting and formatting before writing to a file.
# We avoid this step until now so as to not decrease accuracy in the data.
def preWrite(time_dict, vel_range):
    write_dict = copy.deepcopy(time_dict)
    keys = list(time_dict.keys())
    for k in keys:
        # ANGULAR CASE
        if "ang" in k:
            # Convert the angular data to positive integers
            write_dict[k]["data"] = np.mod(write_dict[k]["data"], 360).astype(int)
        elif "vel" in k:
            write_dict[k]["data"] = array2Bucket(
                write_dict[k]["data"], vel_range
            ).astype(int)
    return write_dict


# Sort the keys of the dictionary
# so the output files are more
# human-readable
def sortKeys(time_dict):
    # Get all keys in the dictionary
    unsorted_keys = list(time_dict.keys())
    # x,y and resolution are hardcoded
    x = "x"
    y = "y"
    r = "resolution"
    # Get all the angular and velocity keys in separate lists
    ang = [a for a in unsorted_keys if "ang" in a]
    vel = [v for v in unsorted_keys if "vel" in v]
    # sort the angular and velocity keys -- this should sort them both the same way
    ang.sort()
    vel.sort()
    # Add the keys into a list
    # and return the new -sorted- key list
    sorted_keys = [r, x, y]  # x,y are always first
    for a, v in zip(ang, vel):
        sorted_keys.append(a)
        sorted_keys.append(v)
    return sorted_keys


# Project coordinates from native projection to web mercator
# This is the only place we use osgeo (ogr)
def projectCoordinates(x, y):
    point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(x, y))
    point.Transform(TRANSFORM)
    coords = point.GetPoint()
    return coords[0], coords[1]  # x,y coords from transformed point


# Write the dictionary to a file
def writeData(time_dict, num_resizes, file_name, write=True):
    # DIVERGENT
    # We have a new flag (write) that will control
    # whether we write the data to a file or just return
    # the data in an array.
    if write:
        # WRITE TO FILE
        with open(file_name, "w+") as f:
            keys = sortKeys(time_dict)
            f.write(",".join(keys) + "\n")
            rows, cols = time_dict["x"][
                "data"
            ].shape  # We could use any key here, they're all the same size
            for i in range(rows):
                for j in range(cols):
                    # Our first argument will be an integer (resolution)
                    # Our next two arguments are floats (x coordinate and y coordinate).
                    # So we format to account for those first.
                    # All other values will be integers so we add non-float formats
                    # for key_length - 3 other arguments (all, but resolution,x and y).
                    form = ["{},{:.0f}", "{:.0f}"] + ["{}"] * (len(keys) - 3)
                    line = ",".join(form) + "\n"
                    # Project the coordinates to web mercator
                    proj_x, proj_y = projectCoordinates(
                        time_dict["x"]["data"][i][j], time_dict["y"]["data"][i][j]
                    )
                    resolution = int(
                        time_dict["resolution"]["data"] * (2 ** num_resizes)
                    )
                    # create the line that we'll be writing to the file
                    values = [resolution, proj_x, proj_y] + [
                        time_dict[k]["data"][i][j] for k in keys[3:]
                    ]  # the 2: skips the first three entries (resolution,unproject x,y)
                    f.write(line.format(*values))
        return True

    else:
        # RETURN DATA IN ARRAY
        # very similar workflow to above, but
        # doesn't open a file and has a
        # useful return value
        keys = sortKeys(time_dict)
        to_be_written = []
        rows, cols = time_dict["x"][
            "data"
        ].shape  # We could use any key here, they're all the same size
        for i in range(rows):
            for j in range(cols):
                # Our first argument will be an integer (resolution)
                # Our next two arguments are floats (x coordinate and y coordinate).
                # So we format to account for those first.
                # All other values will be integers so we add non-float formats
                # for key_length - 3 other arguments (all, but resolution,x and y).
                form = ["{},{:.0f}", "{:.0f}"] + ["{}"] * (len(keys) - 3)
                line = ",".join(form) + "\n"
                # Project the coordinates to web mercator
                proj_x, proj_y = projectCoordinates(
                    time_dict["x"]["data"][i][j], time_dict["y"]["data"][i][j]
                )
                resolution = int(time_dict["resolution"]["data"] * (2 ** num_resizes))
                # create the line that we'll be writing to the file
                values = [resolution, proj_x, proj_y] + [
                    time_dict[k]["data"][i][j] for k in keys[3:]
                ]  # the 2: skips the first three entries (resolution,unproject x,y)
                to_be_written.append(line.format(*values))
        return to_be_written


def jsonData(time_dict, num_resizes):
    keys = sortKeys(time_dict)
    to_be_written = []
    rows, cols = time_dict["x"][
        "data"
    ].shape  # We could use any key here, they're all the same size
    for i in range(rows):
        for j in range(cols):
            # Our first argument will be an integer (resolution)
            # Our next two arguments are floats (x coordinate and y coordinate).
            # So we format to account for those first.
            # All other values will be integers so we add non-float formats
            # for key_length - 3 other arguments (all, but resolution,x and y).
            # form = ["{},{:.0f}","{:.0f}"] + ["{}"]*(len(keys)-3)
            # line = form
            # Project the coordinates to web mercator
            proj_x, proj_y = projectCoordinates(
                time_dict["x"]["data"][i][j], time_dict["y"]["data"][i][j]
            )
            resolution = int(time_dict["resolution"]["data"] * (2 ** num_resizes))
            # create the line that we'll be writing to the file
            values = [resolution, proj_x, proj_y] + [
                time_dict[k]["data"][i][j] for k in keys[3:]
            ]  # the 2: skips the first three entries (resolution,unproject x,y)
            to_be_written.append(values)
    return to_be_written


def createClusters(
    file_dir, write_path, name, wk_id, given_max_vel=None, separate=False, format="csv"
):
    global TRANSFORM
    start = time.time()

    SOURCE_PROJ.ImportFromEPSG(wk_id)
    TRANSFORM = osr.CoordinateTransformation(SOURCE_PROJ, TARGET_PROJ)

    print("Cluster path: {}".format(file_dir))
    FILES_PATH = file_dir
    FILES = [
        os.path.join(FILES_PATH, f)
        for f in os.listdir(FILES_PATH)
        if os.path.isfile(os.path.join(FILES_PATH, f))
        and (f[-7:] == "vel.asc" or f[-7:] == "ang.asc")
    ]

    # If maximum velocity is provided the max_vel here will be that value.
    time_dict, max_vel = createTimeDictionary(FILES, given_max_vel)
    vel_range = createVelocityRange(max_vel)

    format = format.lower()
    if format == "csv":
        if separate:
            write_dict = preWrite(time_dict, vel_range)
            files = []
            write_name = "{}.csv".format(name)
            writeData(write_dict, 0, os.path.join(write_path, write_name))
            files.append(write_name)
            # number of times we've resized the data
            num_resizes = 1

            # use of time_dict["x"] is arbitrary, all keys of time_dict are the same size
            # This will perform imresize until either dimension is 1 (as small as it can get)
            while (
                time_dict["x"]["data"].shape[0] > 1
                and time_dict["x"]["data"].shape[1] > 1
            ):
                time_dict = resizeAll(time_dict)
                write_dict = preWrite(time_dict, vel_range)
                write_name = "{}_{}.csv".format(name, num_resizes)
                writeData(write_dict, num_resizes, os.path.join(write_path, write_name))
                files.append(write_name)
                num_resizes += 1
                # plot.imshow(time_dict["ang_0900"]["data"])
                # plot.show()

        else:
            write_dict = preWrite(time_dict, vel_range)
            keys = sortKeys(write_dict)

            to_write = []
            to_write.append(",".join(keys) + "\n")

            to_write += writeData(write_dict, 0, None, write=False)
            # number of times we've resized the data
            num_resizes = 1
            # use of time_dict["x"] is arbitrary, all keys of time_dict are the same size
            # This will perform imresize until either dimension is 1 (as small as it can get)
            while (
                time_dict["x"]["data"].shape[0] > 1
                and time_dict["x"]["data"].shape[1] > 1
            ):
                time_dict = resizeAll(time_dict)
                write_dict = preWrite(time_dict, vel_range)
                to_write += writeData(write_dict, num_resizes, None, write=False)
                num_resizes += 1
                # plot.imshow(time_dict["ang_0900"]["data"])
                # plot.show()

            # This is a little hokey, but we need to ensure
            # the 'files' values is a list for the return
            files = ["{}_total.csv".format(name)]
            with open(os.path.join(write_path, files[0]), "w+") as f:
                for row in to_write:
                    f.write(row)

    elif format == "json":

        write_dict = preWrite(time_dict, vel_range)

        data = {"header": sortKeys(write_dict), "data": jsonData(write_dict, 0)}

        num_resizes = 1
        while (
            time_dict["x"]["data"].shape[0] > 1 and time_dict["x"]["data"].shape[1] > 1
        ):
            time_dict = resizeAll(time_dict)
            write_dict = preWrite(time_dict, vel_range)
            data["data"] += jsonData(write_dict, num_resizes)
            num_resizes += 1

        files = ["{}_total.json".format(name)]
        json_string = json.dumps(data)
        with open(os.path.join(write_path, files[0]), "w+") as f:
            f.write(json_string)

    else:
        raise ValueError("Unsupported output format: {}".format(format))

    end = time.time()

    v = vel_range.keys()
    v.sort()

    if DEBUG:
        print("runtime: {}".format(end - start))

    return files, v


if __name__ == "__main__":
    file_dir = r"P:\USFS\WindNinja\Source\windninja-mobile-master\WindNinja-Server\Data\job\23becdaadf7c4ec2993497261e63d813\wncli\results"
    name = "clustered"
    createClusters(
        file_dir,
        file_dir,
        name,
        32611,
        given_max_vel=11.09,
        separate=False,
        format="json",
    )
