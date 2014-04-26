package controllers

import play.api._
import play.api.mvc._
import com.mongodb.casbah.Imports._
import com.github.nscala_time.time.Imports._
import com.mongodb.util.JSON
import com.mongodb.casbah.commons.MongoDBObject
import utils.PropertyUtils._


object Application extends Controller {
  
  val MONGO_URL:String="mongodb.url"

  def index = Action {
    Ok(views.html.index("Your new application is ready."))
  }
  
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
    
	val mongoClient = MongoClient("localhost", 27017)
	val db = mongoClient("test")

//    //var url = getProperty(MONGO_URL)
//    val mongoClient = MongoClient(url)
//	val db = mongoClient("pi_security")
	val records = db("records")

	val t = DateTime.now
	val startTime = t.withMinuteOfHour(0).withHourOfDay(0).minusDays(4)
	Logger.debug("startTime: " + startTime)
	val conditionStatement = MongoDBObject("$match" -> MongoDBObject(
			"utcCreateDate" -> MongoDBObject("$gt" -> startTime.toDate())
	))
	
	val projectStatement = MongoDBObject("$project" -> MongoDBObject(
			"year" -> MongoDBObject("$year" -> "$utcCreateDate"),
			"month" -> MongoDBObject("$month" -> "$utcCreateDate"),
			"day" -> MongoDBObject("$dayOfMonth" -> "$utcCreateDate"),
			"hour" -> MongoDBObject("$hour" -> "$utcCreateDate")
	))
	
	val groupStatement = MongoDBObject("$group" -> MongoDBObject(
			"_id" -> MongoDBObject("year" -> "$year", "month" -> "$month", "day" -> "$day", "hour" -> "$hour"),
			"count" -> MongoDBObject("$sum" -> 1)
	))
	    	
	val sortStatement = MongoDBObject("$sort" -> MongoDBObject(
			"_id" -> -1
	))
	
	val pipeLine = List(conditionStatement, projectStatement, groupStatement,sortStatement)
	
	try{
		val allRecords = records.aggregate(pipeLine)
		val jsonData = com.mongodb.util.JSON.serialize(allRecords.results.toList)
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
    finally{
      mongoClient.close()
    }

  }

}