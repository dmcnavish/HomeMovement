name := "HomeMovement"

version := "1.0-SNAPSHOT"

resolvers += "Sonatype releases" at "https://oss.sonatype.org/content/repositories/releases"
//resolvers += "Sonatype snapshots" at "https://oss.sonatype.org/content/repositories/snapshots"

libraryDependencies ++= Seq(
  jdbc,
  anorm,
  cache,
  "org.mongodb" %% "casbah" % "2.7.0" pomOnly(),
  "se.radley" %% "play-plugins-salat" % "1.4.0",
  "com.github.nscala-time" %% "nscala-time" % "0.8.0"
)     

play.Project.playScalaSettings


