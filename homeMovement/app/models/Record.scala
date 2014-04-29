package models

import com.typesafe.config.ConfigFactory
import com.mongodb.casbah.MongoClient
import org.joda.time.DateTime
import play.api.Logger
import com.mongodb.casbah.commons.MongoDBObject
import com.mongodb.casbah.MongoClientURI


case class Record(year: Int, month: Int, day: Int, hour: Int, count: Int)

object Record {
  private val appConf = ConfigFactory.load()
  
  def all(): String = {
    val mongoClient = connectMongo()
//    val db = mongoClient("pi_security")
//    val records = db("records")
    val records = mongoClient("pi_security")("records")

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
	   com.mongodb.util.JSON.serialize(allRecords.results.toList)
	}
    finally{
      mongoClient.close()
    }
  }
  
  def connectMongo(): MongoClient = {
    val mongoDbUrl = appConf.getString("mongodb.url")
    Logger.debug("mongoDbUrl: " + mongoDbUrl)
    val uri = MongoClientURI(mongoDbUrl)
    MongoClient(uri)
  }
}