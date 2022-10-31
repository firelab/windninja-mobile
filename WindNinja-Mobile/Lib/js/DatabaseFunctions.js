//.pragma library


//Esta libreria se ha creado como stateless, por lo que se instanciará solo cuando se necesite.

////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
//////////////////////Basic functions///////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

//Devuelve un manejador de la base de datos
function getHandle(){
    try {
        var db = LocalStorage.openDatabaseSync("WINDNINJA_DB", "", "Local database", 1000000)
    } catch (err) {
        //console.exception("Error opening database: " + err)
    }
    return db
}

//Crea todas las tablas necesarias en la app
function createTables(){
    //console.log("Creating tables if not exist.")
    var db = getHandle()
    try {
        db.transaction(function (tx) {

            //PARAMETERS table
            tx.executeSql('CREATE TABLE IF NOT EXISTS PARAMETERS (' +
                          'KEY TEXT,' +
                          'VALUE TEXT' +
                          ')');

            //console.log("Created table PARAMETERS.")

            //SIMULATION table
            tx.executeSql('CREATE TABLE IF NOT EXISTS SIMULATION (' +
                          'ID_SIM TEXT, ' +
                          'NAME TEXT, ' +
                          'DOWNLOADED NUMERIC, ' +
                          'STATUS TEXT, ' +

                          'MODEL TEXT, ' +
                          'VEGETATION TEXT, ' +
                          'IMPORTED NUMERIC, ' +

                          'VECTOR NUMERIC, ' +
                          'RASTER NUMERIC, ' +
                          'TOPOFIRE NUMERIC, ' +
                          'GEOPDF NUMERIC, ' +
                          'CLUSTERED NUMERIC, ' +
                          'WEATHER NUMERIC, ' +

                          'DURATION REAL, ' +
                          'SUBMITTED_TIMESTAMP TEXT, ' +
                          'INSERTION_TIMESTAMP TEXT, ' +
                          'ERROR_CAUSE TEXT ' +
                          ')');

            //console.log("Created table SIMULATION.")

            //LAYERS table
            tx.executeSql('CREATE TABLE IF NOT EXISTS LAYERS(' +
                          'NAME TEXT, ' +
                          'LAYER_TYPE TEXT, ' +
                          'PATHS TEXT, ' +
                          'IMAGE_PATH TEXT, ' +
                          'DELETABLE REAL ' +
                          ')');

            //console.log("Created table LAYERS.")
        });
        //console.log("All tables created successfully.")
    } catch (err) {
        //console.exception("Error creating tables in the database: " + err)
    };
}

//Elimina todas las tablas de la app
function deleteTables(){
    //console.log("Deleting tables if exist.")
    var db = getHandle()
    try {
        db.transaction(function (tx) {
            tx.executeSql('DROP TABLE IF EXISTS PARAMETERS');
            //console.log("Deleted table: PARAMETERS.")
            tx.executeSql('DROP TABLE IF EXISTS SIMULATION');
            //console.log("Deleted table: SIMULATION.")
            tx.executeSql('DROP TABLE IF EXISTS LAYERS');
            //console.log("Deleted table: LAYERS.")
        })
        //console.log("Deleted all tables from the database.")
    } catch (err) {
        //console.exception("Error deleting tables in the database: " + err)
    };
}

//Restaura la base de datos añadiendo todo lo necesario para su correcto funcionamiento.
function restoreDatabase(){
    //console.log("Restoring Database...")
    try{
        deleteTables();
        createTables();

        //console.log("RestoreDatabase: Saving parameters.")
        saveParameter("VERSION", app.currentVersion)

        //console.log("RestoreDatabase: Inserting values.")
        insertDefaultLayers();

        //console.log("Database restored.")
    }catch(err){
        //console.error("Error restoring the database: " + err)
    }
}





////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
///////////////////Simulations functions////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

//Guarda la simulación indicada en base de datos en caso de que no exista.
function saveSimulation(simulation){
    var db = getHandle();

    if(!simulationExist(simulation.Id_Sim)){
        try{
            db.transaction(function (tx) {
                try{


                    tx.executeSql('INSERT INTO SIMULATION VALUES(?,?,?,?, ?,?,?, ?,?,?,?,?,?, ?,?,?,?)',
                                  [
                                      simulation.Id_Sim,
                                      simulation.Name.replace("\n", " ").replace("\r", " "),
                                      simulation.status,
                                      simulation.downloaded,

                                      simulation.model,
                                      simulation.vegetation,
                                      simulation.imported,

                                      simulation.vector,
                                      simulation.raster,
                                      simulation.topofire,
                                      simulation.geopdf,
                                      simulation.clustered,
                                      simulation.weather,

                                      simulation.Duration,
                                      simulation.subbmitedTimestamp,
                                      simulation.insertionTimestamp,
                                      ""
                                  ]);
                }catch(err){
                    //console.exception("Error inserting simulation " + simulation.Id_Sim + " into database: " + err)
                }
            });
        }catch(err){
            //console.exception("Error inserting simulations into database: " + err)
        }
    }else{
        //console.log("The simulation " + simulation.Name + " currently exist in the database.")
    }
}

//
function createSimulation(simulation){
    var db = getHandle();
    try{
        db.transaction(function (tx) {
            tx.executeSql('INSERT INTO SIMULATION VALUES(?,?,?,?, ?,?,?, ?,?,?,?,?,?, ?,?,?,?)',
                          [
                              simulation.idSim,
                              simulation.name.replace("\n", " ").replace("\r", " "),
                              false,
                              simulation.status,//"new", //"succeeded" //"failed"

                              simulation.model,
                              simulation.vegetation,
                              simulation.imported,

                              simulation.vector,
                              simulation.raster,
                              simulation.topofire,
                              simulation.geopdf,
                              simulation.clustered,
                              simulation.weather,

                              simulation.duration,
                              simulation.subbmitedTimestamp,
                              new Date(),
                              ""
                          ]);
        });
    }catch(err){
        //console.exception("Error inserting simulations into database: " + err)
    }
}

//
function deleteSimulation(idSim){
    var db = getHandle();
    try {
        db.transaction(function (tx) {
            tx.executeSql('DELETE FROM SIMULATION WHERE ID_SIM = ?',[idSim]);
        })
        //console.log("Deleted simulation " + idSim + " from the database.")
    } catch (err) {
        //console.exception("Error deleting simulation " + idSim + " from the database: " + err);
    };
}

//
function deleteNotDownloadedSimulation(idSim){
    var db = getHandle();
    try {
        db.transaction(function (tx) {
            tx.executeSql('DELETE FROM SIMULATION WHERE ID_SIM = ? AND DOWNLOADED = 0',[idSim]);
        })
        //console.log("Deleted simulation " + idSim + " from the database.")
    } catch (err) {
        //console.exception("Error deleting simulation " + idSim + " from the database: " + err);
    };
}

//
function setSimulationStatus(idSim, status){
    var db = getHandle();
    try{
        db.transaction(function (tx) {
            //console.log("Updating simulation status to (" + status + ") for the simulation " + idSim)
            tx.executeSql('UPDATE SIMULATION SET STATUS = ? WHERE ID_SIM = ?',[status, idSim]);
        });
    }catch(err){
        //console.exception("Error updating simulation status (" + status + ") for the simulation " + idSim + "\n" + err)
    }
}

//
function setSimulationSubbmitedTimestamp(idSim, submittedTimestamp){
    var db = getHandle();
    try{
        db.transaction(function (tx) {
            //console.log("Updating simulation submitted timestamp to (" + submittedTimestamp + ") for the simulation " + idSim)
            tx.executeSql('UPDATE SIMULATION SET SUBMITTED_TIMESTAMP = ? WHERE ID_SIM = ?',[submittedTimestamp, idSim]);
        });
    }catch(err){
        //console.exception("Error updating simulation submitted timestamp (" + submittedTimestamp + ") for the simulation " + idSim + "\n" + err)
    }
}

//
function setSimulationModel(idSim, model){
    var db = getHandle();
    try{
        db.transaction(function (tx) {
            //console.log("Updating simulation model to (" + model + ") for the simulation " + idSim)
            tx.executeSql('UPDATE SIMULATION SET MODEL = ? WHERE ID_SIM = ?',[model, idSim]);
        });
    }catch(err){
        //console.exception("Error updating simulation model (" + model + ") for the simulation " + idSim + "\n" + err)
    }
}

//
function setSimulationDuration(idSim, duration){
    var db = getHandle();
    try{
        db.transaction(function (tx) {
            //console.log("Updating simulation duration to " + duration + " for the simulation " + idSim)
            tx.executeSql('UPDATE SIMULATION SET DURATION = ? WHERE ID_SIM = ?',[duration, idSim]);
        });
    }catch(err){
        //console.exception("Error updating simulation duration to " + duration + " for the simulation " + idSim + "\n" + err)
    }
}

function importSimulation(idSim, status, name, subbmitedTimestamp, duration, model, vegetation){
    var _simulation = {
        "idSim" : idSim,
        "status" : status,
        "name" : name,
        "subbmitedTimestamp" : subbmitedTimestamp,
        "model" : model,
        "vegetation" : vegetation,
        "imported" : true,
        "vector" : true,
        "raster" : true,
        "topofire" : true,
        "geopdf" : false,
        "clustered" : false,
        "weather" : true,
        "duration" : duration
    }
    createSimulation(_simulation)
}

function simulationExist(idSim){
    var db = getHandle();
    var result;
    var returnValue = false;
    try{
        db.transaction(function(tx){
            result = tx.executeSql('SELECT * FROM SIMULATION WHERE ID_SIM = ?',[idSim]);
        });
        returnValue = result.rows.length != 0;
    }catch(err){
        //console.exception("Error checking if the parameter " + idSim + " exist in the database: " + err)
    }
    return returnValue;
}

//
function getSimList(nameLike){
    var db = getHandle();
    var returnValue = [];
    var result;
    try{
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT ID_SIM, NAME, IMPORTED, STATUS, DOWNLOADED, DURATION, MODEL, SUBMITTED_TIMESTAMP FROM SIMULATION WHERE NAME LIKE ? ORDER BY SUBMITTED_TIMESTAMP DESC', ['%'+nameLike+'%']);
        })

        for(var i = 0; i<result.rows.length;i++){
            var currentItem = result.rows.item(i);
            returnValue.push({
                                 "idSim":currentItem.ID_SIM,
                                 "name":currentItem.NAME,
                                 "imported":currentItem.IMPORTED,
                                 "status":currentItem.STATUS,
                                 "downloaded":currentItem.DOWNLOADED,
                                 "duration":currentItem.DURATION,
                                 "model":currentItem.MODEL,
                                 "submittedTimestamp":currentItem.SUBMITTED_TIMESTAMP
                             });
        }
    }catch(err){
        //console.exception("Error getting simulations from database: " + err);
    }
    return returnValue;
}

//
function getAllSimsIds(){
    var db = getHandle();
    var returnValue = [];
    var result;
    try{
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT ID_SIM FROM SIMULATION');
        })

        for(var i = 0; i<result.rows.length;i++){
            returnValue.push(result.rows.item(i).ID_SIM);
        }
    }catch(err){
        //console.exception("Error getting simulations IDs from database: " + err);
    }
    return returnValue;
}

//
function getAllPendingSimsIds(){
    var db = getHandle();
    var returnValue = [];
    var result;
    try{
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT ID_SIM FROM SIMULATION WHERE STATUS = ? OR STATUS = ? OR STATUS = ?', ["pending", "new", "executing"]);
        })

        for(var i = 0; i<result.rows.length;i++){
            returnValue.push(result.rows.item(i).ID_SIM);
        }
    }catch(err){
        //console.exception("Error getting simulations IDs from database: " + err);
    }
    return returnValue;
}

//
function setSimulationDownloaded(idSim){
    //console.log("Setting simulation downloaded to sim... " + idSim)
    var db = getHandle();
    try{
        db.transaction(function (tx) {

            tx.executeSql('UPDATE SIMULATION SET DOWNLOADED = ? WHERE REPLACE(ID_SIM, "-", "") = ?',[true, idSim]);
        });
    }catch(err){
        //console.exception("Error seting simulation " + idSim + " downloaded on the database: " + err);
    }
}

//
function getOlderSimulation(){
    var db = getHandle();
    var result;
    var returnValue;
    try {
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT ID_SIM FROM SIMULATION ORDER BY SUBMITTED_TIMESTAMP ASC LIMIT 1');
            returnValue = result.rows.item(0).ID_SIM;
        })
    } catch (err) {
        returnValue = ""
        //console.exception("Error getting the older simulation from the database: " + err);
    };
    return returnValue;
}


//
function getErrorCause(idSim){
    var db = getHandle();
    var result;
    var returnValue;
    try {
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT ERROR_CAUSE FROM SIMULATION WHERE ID_SIM = ?',[idSim]);
            returnValue = result.rows.item(0).ERROR_CAUSE;
        })
    } catch (err) {
        returnValue = ""
        //console.exception("Error getting the ERROR_CAUSE from the database: " + err);
    };
    return returnValue;
}

//
function setErrorCause(idSim, errorCause){
    var db = getHandle();
    var result;
    try{
        db.transaction(function (tx) {
            //console.log("Updating ERROR_CAUSE " + idSim + " from the database.")
            try{
                tx.executeSql('UPDATE SIMULATION SET ERROR_CAUSE = ? WHERE ID_SIM = ?',[errorCause, idSim]);
            }catch(err){
                //console.exception("Error updating ERROR_CAUSE " + idSim + " from database: " + err)
            }
        });
    }catch(err){
        //console.exception("Error inserting values into database: " + err)
    }
}







////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
//////////////////////Layers functions//////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

//Añade una ruta de un fichero TPK a la base de datos.
function addLayers(name, layerType, paths, imagePath, deletable){
    var db = getHandle();
    var result;
    name = name.split(".")[0];
    try{
        db.transaction(function (tx) {
            if(layerExist(name)){
                //console.log("Updating layer " + name + " from the database. New pats " + paths)
                try{
                    tx.executeSql('UPDATE LAYERS SET PATHS = ? WHERE NAME = ?',[paths, name]);
                }catch(err){
                    //console.exception("Error updating layer " + name + " from database: " + err)
                }
            }else{
                //console.log("Inserting layer " + name + " into the database with paths " + paths)
                try{
                    var stringifyPaths = paths.toString()
                    //console.log(stringifyPaths)
                    tx.executeSql('INSERT INTO LAYERS VALUES(?,?,?,?,?)',[name, layerType, stringifyPaths, imagePath, deletable]);
                }catch(err){
                    //console.exception("Error inserting layer " + name + " into database: " + err)
                }
            }
        });
    }catch(err){
        //console.exception("Error inserting layers into database: " + err)
    }
}

//Comprueba si una capa existe en la base de datos.
function layerExist(name){
    var db = getHandle();
    var result;
    var returnValue = false;
    try{
        db.transaction(function(tx){
            result = tx.executeSql('SELECT * FROM LAYERS WHERE NAME = ?',[name]);
        });
        returnValue = result.rows.length != 0;
    }catch(err){
        //console.exception("Error checking if the layer " + name + " exist in the database: " + err)
    }
    return returnValue;
}

//Elimina una entrada de la tabla de Layers.
function deleteLayers(name){
    var db = getHandle();
    try {
        db.transaction(function (tx) {
            tx.executeSql('DELETE FROM LAYERS WHERE NAME = ?',[name]);
        })
        //console.log("Deleted base map " + name + " from the database.")
    } catch (err) {
        //console.exception("Error deleting base map " + name + " from the database: " + err);
    };
}

//Obtiene un array con todas las capas de la base de datos.
function getAllLayers(){
    var db = getHandle();
    var returnValue = [];
    var result;
    try{
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT NAME, LAYER_TYPE, PATHS, IMAGE_PATH, DELETABLE FROM LAYERS');
        })
    }catch(err){
        //console.exception("Error getting base maps from database: " + err);
    }

    for(var i = 0; i<result.rows.length;i++){

        var currentItem = result.rows.item(i);

        var name=currentItem.NAME;
        var layerType = currentItem.LAYER_TYPE;
        var paths=currentItem.PATHS;
        var imagePath=currentItem.IMAGE_PATH;
        var deletable=currentItem.DELETABLE

        returnValue.push({
                             "name":name,
                             "layerType":layerType,
                             "paths":paths,
                             "imagePath":imagePath,
                             "deletable":deletable
                         });
    }
    return returnValue;
}

//Devuelve cuantas capas hay en base de datos.
function countLayers(){
    var db = getHandle();
    var returnValue = 0;
    var result;
    try{
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT COUNT(*) AS TOTAL FROM LAYERS');
        })
    }catch(err){
        //console.exception("Error counting base maps from database: " + err);
    }

    returnValue = result.rows.item(0).TOTAL

    return returnValue;
}

//Inserta en base de datos las capas por defecto.
function insertDefaultLayers(){

    //console.log("Adding default layers to the database.")
    addLayers("Imagery", "ArcGISTiledLayer", ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer", "https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer"], "../Assets/Map/world-imagery.jpg",0);
    addLayers("Terrain", "ArcGISTiledLayer", ["https://services.arcgisonline.com/arcgis/rest/services/World_Terrain_Base/MapServer","https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Reference_Overlay/MapServer"], "../Assets/Map/world-terrain.jpg",0);
    addLayers("World Topo", "ArcGISTiledLayer", ["https://services.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer"], "../Assets/Map/world-topo.jpg",0);
    addLayers("TopoFire", "WebTiledLayer", ["https://topofire.dbs.umt.edu/topofire_v2/data/osmUShydro/{level}/{col}/{row}.png"], "../Assets/Map/topo-fire.jpg",0);
    addLayers("US Topo", "ArcGISTiledLayer", ["https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer"], "../Assets/Map/us-topo.jpg",0);
    addLayers("Fuel Models", "", [""], "../Assets/Map/fuels-model.jpg",0);
    //console.log("Added default layers.");
}





////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
////////////////////Parameters functions////////////////////
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////

//Guarda el parametro indicado en base de datos
function saveParameter(key, value){
    var db = getHandle();
    var result;
    try{
        db.transaction(function (tx) {
            if(parameterExist(key)){
                //console.log("Updating parameter " + key + " from the database. New value " + value)
                try{
                    tx.executeSql('UPDATE PARAMETERS SET VALUE = ? WHERE KEY = ?',[value, key]);
                }catch(err){
                    //console.exception("Error updating parameter " + key + " from database: " + err)
                }
            }else{
                //console.log("Inserting parameter " + key + " into the database with value " + value)
                try{
                    tx.executeSql('INSERT INTO PARAMETERS VALUES(?,?)',[key, value]);
                }catch(err){
                    //console.exception("Error inserting parameter " + key + " into database: " + err)
                }
            }
        });
    }catch(err){
        //console.exception("Error inserting values into database: " + err)
    }
}

//Devuelve el valor del parametro indicado de la base de datos
function getParameter(key){
    var db = getHandle();
    var result;
    var returnValue;
    try {
        db.transaction(function (tx) {
            result = tx.executeSql('SELECT VALUE FROM PARAMETERS WHERE KEY = ?',[key]);
            returnValue = result.rows.item(0).VALUE
        })
    } catch (err) {
        returnValue = ""
        //console.exception("Error getting parameter " + key + " from the database: " + err);
    };
    return returnValue;
}

//Elimina el parametro indicado de la base de datos
function deleteParameter(key){
    var db = getHandle();
    try {
        db.transaction(function (tx) {
            tx.executeSql('DELETE FROM PARAMETERS WHERE KEY = ?',[key]);
        })
        //console.log("Deleted parameter " + key + " from the database.")
    } catch (err) {
        //console.exception("Error deleting parameter " + key + " from the database: " + err);
    };
}

//Devuelve un boolean indicando si ese parametro existe en base de datos.
function parameterExist(key){
    var db = getHandle();
    var result;
    var returnValue = false;
    try{
        db.transaction(function(tx){
            result = tx.executeSql('SELECT * FROM PARAMETERS WHERE KEY = ?',[key]);
        });
        returnValue = result.rows.length != 0;
    }catch(err){
        //console.exception("Error checking if the parameter " + key + " exist in the database: " + err)
    }
    return returnValue;
}


























