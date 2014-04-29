package controllers

import play.api._
import play.api.mvc._
import com.mongodb.casbah.Imports._
import com.github.nscala_time.time.Imports._
import com.mongodb.util.JSON
import com.mongodb.casbah.commons.MongoDBObject
import utils.PropertyUtils._
import models.Record


object Application extends Controller {
  def index = Action {
    Ok(views.html.index("Your new application is ready."))
  }
  
  //FOR TESTING
  def createRecords = Action {
    val mongoClient = MongoClient("localhost", 27017)
	val db = mongoClient("test")
	val records = db("records")
	
    val t = DateTime.now
	for (i <- 1 to 100){
		val createDate = t.minusHours(i)
		val r = MongoDBObject("utcCreateDate" -> createDate.toDate(), "x" -> i* 3, "y" -> i*5)
		records.insert(r)
	}
    
    Ok("Records Inserted")
  }

  def getRecords = Action {
	try{
		val jsonData = Record.all()
//		Logger.debug(jsonData)
		Ok(jsonData)
	}
    catch{
      case e: Exception if(e.getMessage().contains("Unable to connect to any servers")) => {
        Logger.error("Error retrieving records", e)
        Ok("[{error:'Error connecting to database server.'}]") //TODO: return error json message
      }
      case e: Throwable => {
        Logger.error("Error retrieving results", e)
        Ok("[{error:'Error retrieving results.'}]") //TODO: return error json message
      }
      
      
    }

  }

}