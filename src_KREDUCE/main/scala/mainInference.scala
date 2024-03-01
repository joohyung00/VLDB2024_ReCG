package parametric
import parametric.typeReduction._
import parametric.typeInference._
import parametric.typeDefinition._
import java.io._

import play.api.libs.json._
import scala.io.Source

object mainInference {

    val usage =
        """Usage: <path> <equiv> 
        """.stripMargin

    def main(args: Array[String]): Unit = 
    {
        if (args.length < 2) 
        {
            println(usage)
            System.exit(0)
        }
        val filename = args(0)
        val equiv = args(1)

        val startTime = System.currentTimeMillis() // Start timer

        // read the input jsonlines
        val file = Source.fromFile(filename)
        val jsonlines = file.getLines.toList
        val nbLines = jsonlines.length
        println(s"read $nbLines lines of $filename")

        /** infer the schema */
        val helper = new Helper()
        val order = helper.whichOrdering(equiv)
        val formatter = new Formatter()

        val reducer = new Reduction()
        val inferencer = new Inference()

        val parsed = jsonlines.filter(x => x.length() > 0).map { x =>
            try Json.parse(x.stripMargin)
            catch 
            {
                case e: Throwable => e.printStackTrace(); JsNull
                // a quick trick to avoid crashing the app TODO improve
            }
        }
        val nbParsed = parsed.length
        println(s"inferring $equiv schema for $nbParsed parsed objects")

        val types = parsed.map(x =>
            inferencer
                .inferStructType(x, reducer.Reduce, order)
                .asInstanceOf[countingType]
        )
        val result: countingType =
        types.reduce((t, u) => reducer.Reduce(t, u, order))

        val formatted = formatter.typeToJsonMD(result, nbParsed, Map())
        // println(s"$formatted")

        val endTime = System.currentTimeMillis() // End Timer

        val pw = new PrintWriter(new File("hello.txt"))
        pw.write(s"$formatted")
        pw.write("\n")
        pw.write((endTime - startTime).toString())
        val total_time_in_string = (endTime - startTime).toString()
        println(s"Total Time: $total_time_in_string")
        pw.close

        file.close
    }
}
