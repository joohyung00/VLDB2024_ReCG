import java.io._
import java.util.Calendar
import scala.Console


import Extractor.Types.{AttributeName, BiMaxNode, BiMaxStruct, DisjointNodes}
import org.apache.spark.rdd.RDD
import util.NodeToJsonSchema
import Extractor._
import org.spark_project.dmg.pmml.OutputField.Algorithm
import util.Log
import org.apache.spark.sql.functions.col

import scala.collection.mutable


//
import java.io.FileWriter
import Extractor.{Attribute, Extract, JE_Boolean, JE_Numeric, JE_String, JacksonShredder, JsonExplorerType}
import util.Log.LogOutput
//


object SparkMain {

  // //
  // private def shredRecords(input: RDD[String]): RDD[JsonExplorerType] =
  //   input.mapPartitions(x=>JacksonShredder.shred(x))

  // private def extractTypeStructure(shreddedRecords: RDD[JsonExplorerType]): Set[JsonExplorerType] =
  //   shreddedRecords.distinct().collect().toSet

  // private def validateRows(schemas: Set[JsonExplorerType], validationSet: RDD[String]): Double = {
  //   val validationSetSize: Double = validationSet.count().toDouble
  //   if(validationSetSize > 0)
  //     return shredRecords(validationSet).map(x => if(schemas.contains(x)) 1.0 else 0.0).reduce(_+_) / validationSetSize
  //   else return 0.0
  // }

  // def run(train: RDD[String], validate: RDD[String], log: mutable.ListBuffer[LogOutput]): Unit = {
  //   val schemas = extractTypeStructure(shredRecords(train)) // issue with multiple different types and nulls

  //   // println("schemas")
  //   // schemas.foreach(println)
  //   // println("validate")
  //   // validate.collect().foreach(println)

  //   log += LogOutput("Precision", schemas.size.toString, "Precision: ")
  //   log += LogOutput("Recall", validateRows(schemas, validate).toString(), "Recall: ")
  //   log += LogOutput("Grouping", schemas.size.toString(), "Grouping: ")
  // }
  //




  def main(args: Array[String]): Unit = {

    Log.add("Date", Calendar.getInstance().getTime().toString)

    // Creates spark session
    // Makes train set
    // Makes validation set
    val config = util.CMDLineParser.readArgs(args) // Creates the Spark session with its config values.

    Log.add("input file", config.fileName.replace("\\","/"))

    val startTime = System.currentTimeMillis() // Start timer

    val log: mutable.ListBuffer[LogOutput] = mutable.ListBuffer[LogOutput]()

    //println("This is train")
    //println(config.train.collect().foreach(println))
    //println("train ends")

    // 
    //run(config.train, config.validation, log)

    // log += LogOutput("TrainPercent",config.trainPercent.toString,"TrainPercent: ")
    // log += LogOutput("ValidationSize",config.validationSize.toString,"ValidationSize: ")
    // log += LogOutput("Algorithm","verbose","Algorithm: ")
    // log += LogOutput("Seed",config.seed match {
    //   case Some(i) => i.toString
    //   case None => "None"},"Seed: ")

    // config.spark.conf.getAll.foreach{case(k,v) => log += LogOutput(k,v,k+": ")}
    // log += LogOutput("kse",config.kse.toString,"KSE: ")

    // val logFile = new FileWriter(config.logFileName, true)
    // logFile.write("{" + log.map(_.toJson).mkString(",") + "}\n")
    // logFile.close()
    // // println(log.map(_.toString).mkString("\n"))
    // //





      ///////////////////////////////////////////////////////////////
      /// 1. Extract complex schemas - varObjs, objArrs           ///
      ///////////////////////////////////////////////////////////////

    val start_1 = System.currentTimeMillis()

    val calculateEntropy = true

    val (variableObjs, objArrs): (Set[AttributeName],Set[AttributeName]) = 
    if(calculateEntropy) 
    {
      RunExplorer.extractComplexSchemas(config,startTime)
    } 
    else 
    {
      (Set[AttributeName](), Set[AttributeName]())
    }

    // ADDED HERE
    //
    // val str_varObjs = variableObjs.mkString("\n")
    // val str_objArrs = objArrs.mkString("\n")
    // 
    // println("variable Objects")
    // println(str_varObjs)
    // println("object arrays")
    // println(str_objArrs)
    //
    //

    val end_1 = System.currentTimeMillis()
    val runtime_1 = end_1 - start_1
    Log.add("1. Extract Complex Schemas", runtime_1.toString())






      ///////////////////////////////////////////////////////////////
      /// 2. Generate feature vectors                             ///
      ///////////////////////////////////////////////////////////////

    val secondPassStart = System.currentTimeMillis()

    val shreddedRecords: RDD[JsonExplorerType] = RunExplorer.shredRecords(config.train)

    // ADDED HERE
    //
    // println("Shredded Records!")
    // println("/////////////////")
    // shreddedRecords.collect().foreach(println)
    // println("/////////////////")
    // println("Shredded Records Ends")
    //
    //


    // create feature vectors, currently should work if schemas generated from subset of training data
    val featureVectors: Array[(
        AttributeName, 
        Either[
            mutable.HashMap[Map[AttributeName,mutable.Set[JsonExplorerType]],Int], 
            mutable.HashMap[AttributeName,(mutable.Set[JsonExplorerType],Int)]]
        )] =
      shreddedRecords.flatMap(FeatureVectors.shredJET(variableObjs, objArrs, _))
        .combineByKey(x => FeatureVectors.createCombiner(variableObjs, objArrs, x), FeatureVectors.mergeValue, FeatureVectors.mergeCombiners).collect()

    
    // ADDED HERE
    //
    // println("Feature Vectors!")
    // println("/////////////////")
    // featureVectors.foreach(println)
    // println("/////////////////")
    // println("Feature Vectors Ends")
    // Log.add("Feature Vectors", featureVectors.mkString("\n"))
    //
    //

    val fvTime = System.currentTimeMillis()
    val fvRunTime = fvTime - secondPassStart
    Log.add("2. Generate Feature Vectors", fvRunTime.toString())



    var algorithmSchema = ""

    if(config.runBiMax.equals(util.CMDLineParser.BiMax))
    {

      ///////////////////////////////////////////////////////////////
      /// 3. Bimax                                                ///
      ///////////////////////////////////////////////////////////////

      val start_3 = System.currentTimeMillis()
      
      // BiMax algorithm
      val rawSchemas: Map[AttributeName, Types.DisjointNodes] = 
      featureVectors.map(x => {
        x._2 match 
        {
          case Left(l) => 
            (
              x._1, 
              BiMax.OurBiMax.bin(l),   // DisjointNodes -> BimaxStruct -> BimaxNode
              true
            )
          
          //// DON'T DO BIMAX ON VAR_OBJECTS
          case Right(r) =>
            (
              x._1, // _1
              mutable.Seq(
                mutable.Seq(BiMaxNode(
                                      Set[AttributeName](), 
                                      Map[AttributeName, mutable.Set[JsonExplorerType]](), 
                                      0, 
                                      r.map(x => (Map[AttributeName, mutable.Set[JsonExplorerType]]((x._1, x._2._1)), x._2._2)).toList.to[mutable.ListBuffer]
                                      )
                )
              ),    // _2
              false // _3
              // don't do bimax on var_objects
            )
        }
      }).map(
        x => 
          if (x._3) 
            (x._1, BiMax.OurBiMax.rewrite(x._2, config.fast))
          else 
            (x._1, x._2)
      ).toMap
      // val disjointNodes: mutable.ListBuffer[BiMaxStruct] = mutable.ListBuffer[BiMaxStruct]()
      // type BiMaxStruct = mutable.Seq[BiMaxNode]

      val end_3 = System.currentTimeMillis()
      val runtime_3 = end_3 - start_3
      Log.add("3. Bimax", runtime_3.toString())

      // ADDED HERE
      //
      // println("Raw Schemas")
      // println("/////////////////")
      // rawSchemas.foreach( {case (key, value) => println(key + "-->" + value)} )
      // println("/////////////////")
      // println("Raw Schemas Ends")
      // Log.add("Raw Schemas", rawSchemas.mkString("\n"))
      //
      //







      ///////////////////////////////////////////////////////////////
      /// 4. Merge Schemas                                        ///
      ///////////////////////////////////////////////////////////////

      //TODO track basic types from raw schemas
      // combine subset types for each attribute

      val start_4 = System.currentTimeMillis()

      val mergedSchemas: Map[AttributeName, DisjointNodes] = 
        rawSchemas.map{
          case(name, djn) => 
            (name, djn.map( bms => bms.map(NodeToJsonSchema.biMaxNodeTypeMerger(_)) ))
        }

      val end_4 = System.currentTimeMillis()
      val runtime_4 = end_4 - start_4
      Log.add("4. Merge Schemas", runtime_4.toString())

      // ADDED HERE
      //
      // println("Merged Schemas")
      // println("/////////////////")
      // mergedSchemas.foreach({case (key, value) => println(key + "-->" + value)})
      // println("/////////////////")
      // println("Merged Schemas Ends")
      // Log.add("Merged Schemas", mergedSchemas.mkString("\n"))
      //
      //










      ///////////////////////////////////////////////////////////////
      /// 5. Variable Objs With Mult                              ///
      ///////////////////////////////////////////////////////////////

      val start_5 = System.currentTimeMillis()

      val variableObjWithMult: Map[AttributeName,(mutable.Set[JsonExplorerType],Int)] = 
      variableObjs
        .map(varObjName => {val m = mergedSchemas
          .map(djn => { val d = djn._2
            .flatMap(possibleSchemas => possibleSchemas
              .map(z => {
                
                val first =
                  if(z.multiplicity > 0) 
                    z.types.get(varObjName) match 
                    {
                      case Some(v) => (v,z.multiplicity) 
                      case None => (mutable.Set[JsonExplorerType](),0)
                    } 
                  else 
                    (mutable.Set[JsonExplorerType](), 0)
                    
                val sec = 
                  if(z.subsets.nonEmpty) 
                    z.subsets.map(sub =>  if (sub._1.contains(varObjName)) 
                                            (sub._1.get(varObjName).get,sub._2)
                                          else 
                                            (mutable.Set[JsonExplorerType](),0)).reduce((l:(mutable.Set[JsonExplorerType],Int),r:(mutable.Set[JsonExplorerType],Int)) => (l._1 ++ r._1, l._2 + r._2))
                  else (mutable.Set[JsonExplorerType](),0)
                
                (first._1 ++ sec._1, first._2 + sec._2)
              })
            )
            d
          })

          (varObjName, m.flatten.reduce((l, r) => (l._1 ++ r._1, l._2 + r._2)))
        }
      ).toMap


      val end_5 = System.currentTimeMillis()
      val runtime_5 = end_5 - start_5
      Log.add("5. Variable Objs With Mult", runtime_5.toString())

    //   def reduceTypes(s: mutable.Set[JsonExplorerType]): mutable.Set[JsonExplorerType] = {
    //     if(s.size == 1)
    //       return s
    //     val typesWithoutEmpty = s.filter(t => 
    //                                         if (t.equals(JE_Empty_Object) && s.contains(JE_Object) || (t.equals(JE_Empty_Array) && s.contains(JE_Array))) false 
    //                                         else true
    //                                     )
    //     val types = typesWithoutEmpty.filter(t => 
    //                                             if (t.equals(JE_Null) && typesWithoutEmpty.size == 2) false 
    //                                             else true
    //                                         )
    //     return types
    //   }


    //   val reducedMergedSchemas = 
    //   mergedSchemas.map(
    //     x => (x._1, x._2.map(
    //       y => y.map(
    //         z => {
    //           BiMaxNode(
    //             z.schema,
    //             z.types.map(r => (r._1, reduceTypes(r._2))),
    //             z.multiplicity,
    //             z.subsets
    //           )
    //         }
    //       )
    //     )
    //     )
    //   )
      //util.JsonSchemaToJsonTable.convert(reducedMergedSchemas, variableObjs, objArrs)
      

      ///////////////////////////////////////////////////////////////
      /// 6. Bimax Node to Schema                                 ///
      ///////////////////////////////////////////////////////////////

      val start_6 = System.currentTimeMillis()

      val JsonSchema: util.JsonSchema.JSS = util.NodeToJsonSchema.biMaxToJsonSchema(mergedSchemas, variableObjWithMult, objArrs)
      algorithmSchema = JsonSchema.toString  + "\n"

      val end_6 = System.currentTimeMillis()
      val runtime_6 = end_6 - start_6
      Log.add("6. Variable Objs With Mult", runtime_6.toString())
    } 



    else if(config.runBiMax.equals(util.CMDLineParser.Subset)) 
    {
      // onlySubSet test
      val onlySubset: Map[AttributeName, Types.DisjointNodes] = featureVectors.map(x => {
        x._2 match {
          case Left(l) => (x._1, BiMax.OurBiMax.bin(l), true)
          case Right(r) =>
            (x._1,
              mutable.Seq(mutable.Seq(
                BiMaxNode(Set[AttributeName](), Map[AttributeName, mutable.Set[JsonExplorerType]](), 0, r.map(x => (Map[AttributeName, mutable.Set[JsonExplorerType]]((x._1, x._2._1)), x._2._2)).toList.to[mutable.ListBuffer])
              )), false // don't do bimax on var_objects
            )
        }

      })
        .map(x => (x._1, x._2)).toMap

      val variableObjWithMult: Map[AttributeName,(mutable.Set[JsonExplorerType],Int)] = variableObjs
        .map(varObjName => {val m = onlySubset
          .map(djn => { val d = djn._2
            .flatMap(possibleSchemas => possibleSchemas
              .map(z => {
                val first = if (z.multiplicity > 0) z.types.get(varObjName) match {case Some(v) => (v,z.multiplicity) case None => (mutable.Set[JsonExplorerType](),0)} else (mutable.Set[JsonExplorerType](),0)
                val sec = if(z.subsets.nonEmpty) z.subsets.map(sub => if (sub._1.contains(varObjName)) (sub._1.get(varObjName).get,sub._2) else (mutable.Set[JsonExplorerType](),0)).reduce((l:(mutable.Set[JsonExplorerType],Int),r:(mutable.Set[JsonExplorerType],Int)) => (l._1 ++ r._1, l._2 + r._2))
                else (mutable.Set[JsonExplorerType](),0)
                (first._1 ++ sec._1,first._2+sec._2)
              })
            )
            d
          })

          (varObjName,m.flatten.reduce((l,r) => (l._1 ++ r._1, l._2 + r._2)))
        }).toMap

      val JsonSchema: util.JsonSchema.JSS = util.NodeToJsonSchema.biMaxToJsonSchema(onlySubset,variableObjWithMult, objArrs)
      algorithmSchema = JsonSchema.toString  + "\n"
    } 
    
    else if(config.runBiMax.equals(util.CMDLineParser.Verbose)){
      val rawSchemas: Map[AttributeName,Types.DisjointNodes] = featureVectors.map(x => {
        x._2 match {
          case Left(l) =>
            (x._1,
              mutable.Seq[BiMaxStruct](l.map(x => BiMaxNode(
                x._1.map(_._1).toSet,
                x._1,
                x._2,
                mutable.ListBuffer[(Map[AttributeName,mutable.Set[JsonExplorerType]],Int)]()
              )).toSeq.to[mutable.Seq]
              )
            )

          case Right(r) =>
            (x._1,
              mutable.Seq(mutable.Seq(
                BiMaxNode(Set[AttributeName](),Map[AttributeName,mutable.Set[JsonExplorerType]](),0,r.map(x => (Map[AttributeName,mutable.Set[JsonExplorerType]]((x._1,x._2._1)),x._2._2)).toList.to[mutable.ListBuffer])
              )) // don't do bimax on var_objects
            )
        }

      }).toMap

      val variableObjWithMult: Map[AttributeName,(mutable.Set[JsonExplorerType],Int)] = variableObjs
        .map(varObjName => {val m = rawSchemas
          .map(djn => { val d = djn._2
            .flatMap(possibleSchemas => possibleSchemas
              .map(z => {
                val first = if (z.multiplicity > 0) z.types.get(varObjName) match {case Some(v) => (v,z.multiplicity) case None => (mutable.Set[JsonExplorerType](),0)} else (mutable.Set[JsonExplorerType](),0)
                val sec = if(z.subsets.nonEmpty) z.subsets.map(sub => if (sub._1.contains(varObjName)) (sub._1.get(varObjName).get,sub._2) else (mutable.Set[JsonExplorerType](),0)).reduce((l:(mutable.Set[JsonExplorerType],Int),r:(mutable.Set[JsonExplorerType],Int)) => (l._1 ++ r._1, l._2 + r._2))
                else (mutable.Set[JsonExplorerType](),0)
                (first._1 ++ sec._1,first._2+sec._2)
              })
            )
            d
          })

          (varObjName,m.flatten.reduce((l,r) => (l._1 ++ r._1, l._2 + r._2)))
        }).toMap

      val JsonSchema: util.JsonSchema.JSS = util.NodeToJsonSchema.biMaxToJsonSchema(rawSchemas,variableObjWithMult, objArrs)
      algorithmSchema = JsonSchema.toString  + "\n"
    } 

    else if(config.runBiMax.equals(util.CMDLineParser.kmeans) || config.runBiMax.equals(util.CMDLineParser.Hierarchical)){
      // BiMax algorithm
      val k = 6

      val intemediateResult : Seq[(AttributeName, DisjointNodes, Boolean)] = featureVectors.map(x => {
        x._2 match {
          case Left(l) =>
            //Type mismatch. Required: String, found: mutable.HashMap[Map[AttributeName, mutable.Set[JsonExplorerType]], Int]
            //Type mismatch. Required: String, found: mutable.HashMap[AttributeName, (mutable.Set[JsonExplorerType], Int)]
            if(x._1.isEmpty) 
            { // only do k-means on root to give it the best chance
              (x._1, Exec.Algorithms.toDisjointNodes(l), true)
            } 
            else 
            {
                val attributeMap: mutable.HashMap[AttributeName, (mutable.Set[JsonExplorerType], Int)] = mutable.HashMap[AttributeName, (mutable.Set[JsonExplorerType], Int)]()

                l.foreach
                {
                    case(row, count) => row.foreach
                    {
                        case(name, types) => 
                        {
                            attributeMap.get(name) match 
                            {
                                case Some(attributeStats) => types.foreach( typ => { if(!attributeStats._1.contains(typ)) attributeStats._1.add(typ) } )
                                    attributeMap.put(name,(attributeStats._1,attributeStats._2+count))

                                case None =>
                                    attributeMap.put(name,(types,count))
                            }
                        }
                    }
                }
                (x._1,
                    mutable.Seq(mutable.Seq(
                    BiMaxNode(Set[AttributeName](),Map[AttributeName,mutable.Set[JsonExplorerType]](),0,attributeMap.map(x => (Map[AttributeName,mutable.Set[JsonExplorerType]]((x._1,x._2._1)),x._2._2)).toList.to[mutable.ListBuffer])
                    )), false // flatten non-root
                )
            }
          case Right(r) =>
            (
                x._1,
                mutable.Seq(mutable.Seq(
                    BiMaxNode(Set[AttributeName](),Map[AttributeName,mutable.Set[JsonExplorerType]](),0,r.map(x => (Map[AttributeName,mutable.Set[JsonExplorerType]]((x._1,x._2._1)),x._2._2)).toList.to[mutable.ListBuffer])
                )), 
                false // flatten var_objects
            )
        }

      })

        // HERE : KMeans Inspection 
        // val bFile = new File("b.txt")
        // val outputStream = new FileOutputStream(bFile)
        // val printStream = new PrintStream(outputStream)

        // // Save the original standard output
        // val originalOut = Console.out

        // // Redirect standard output to the file
        // Console.setOut(printStream)

        // // Your println statements go here
        // println("<<<<<<<<<<<<<<Intermediate Results>>>>>>>>>>>>>")
        // intemediateResult.foreach(println)
        // println("")

        // // Flush and close the print stream after writing
        // printStream.flush()
        // printStream.close()

        // // Restore the original standard output
        // Console.setOut(originalOut)
        // outputStream.close()
        

        val rawSchemas : Map[AttributeName, Types.DisjointNodes] = intemediateResult.map(x => 
            if (x._3) 
            (
                x._1,
                if(config.runBiMax.equals(util.CMDLineParser.kmeans)) 
                    Exec.Algorithms.runKMeans(config.spark.sparkContext, x._2, k) 
                else 
                    Exec.Algorithms.runHierachical(config.spark.sparkContext,x._2,k)
            ) 
            else 
            (x._1, x._2)
        ).toMap
      

      //TODO track basic types from raw schemas

      // combine subset types for each attribute
      val mergedSchemas:  Map[AttributeName,DisjointNodes] = rawSchemas.map{case(name,djn) => (name,djn.map(bms => bms.map(NodeToJsonSchema.biMaxNodeTypeMerger(_))))}

      val variableObjWithMult: Map[AttributeName,(mutable.Set[JsonExplorerType],Int)] = variableObjs
        .map(varObjName => {val m = mergedSchemas
          .map(djn => { val d = djn._2
            .flatMap(possibleSchemas => possibleSchemas
              .map(z => {
                val first = if (z.multiplicity > 0) z.types.get(varObjName) match {case Some(v) => (v,z.multiplicity) case None => (mutable.Set[JsonExplorerType](),0)} else (mutable.Set[JsonExplorerType](),0)
                val sec = if(z.subsets.nonEmpty) z.subsets.map(sub => if (sub._1.contains(varObjName)) (sub._1.get(varObjName).get,sub._2) else (mutable.Set[JsonExplorerType](),0)).reduce((l:(mutable.Set[JsonExplorerType],Int),r:(mutable.Set[JsonExplorerType],Int)) => (l._1 ++ r._1, l._2 + r._2))
                else (mutable.Set[JsonExplorerType](),0)
                (first._1 ++ sec._1,first._2+sec._2)
              })
            )
            d
          })

          (varObjName,m.flatten.reduce((l,r) => (l._1 ++ r._1, l._2 + r._2)))
        }).toMap


      def reduceTypes(s: mutable.Set[JsonExplorerType]): mutable.Set[JsonExplorerType] = {
        if(s.size == 1)
          return s
        val typesWithoutEmpty = s.filter( t => if (t.equals(JE_Empty_Object) && s.contains(JE_Object) || (t.equals(JE_Empty_Array) && s.contains(JE_Array))) false else true)
        val types = typesWithoutEmpty.filter( t => if (t.equals(JE_Null) && typesWithoutEmpty.size == 2) false else true)
        return types
      }

      val reducedMergedSchemas = mergedSchemas.map(x => (x._1,x._2.map(y => y.map(z => {
        BiMaxNode(z.schema,
          z.types.map(r => (r._1, reduceTypes(r._2))),
          z.multiplicity,
          z.subsets
        )

      }))))
      //util.JsonSchemaToJsonTable.convert(reducedMergedSchemas, variableObjs, objArrs)
      val JsonSchema: util.JsonSchema.JSS = util.NodeToJsonSchema.biMaxToJsonSchema(mergedSchemas,variableObjWithMult, objArrs)
      algorithmSchema = JsonSchema.toString  + "\n"
    }

    else if(config.runBiMax.equals(util.CMDLineParser.Flat)){
      // BiMax algorithm
      val rawSchemas: Map[AttributeName,Types.DisjointNodes] = featureVectors.map(x => {
        x._2 match {
          case Left(l) =>
              val attributeMap: mutable.HashMap[AttributeName, (mutable.Set[JsonExplorerType], Int)] = mutable.HashMap[AttributeName, (mutable.Set[JsonExplorerType], Int)]()
              l.foreach{case(row,count) =>
                row.foreach{case(name,types) => {
                  attributeMap.get(name) match {
                    case Some(attributeStats) =>
                      types.foreach(typ => {
                        if(!attributeStats._1.contains(typ))
                          attributeStats._1.add(typ)
                      })
                      attributeMap.put(name,(attributeStats._1,attributeStats._2+count))
                    case None =>
                      attributeMap.put(name,(types,count))
                  }
                }}
              }
              (x._1,
                mutable.Seq(mutable.Seq(
                  BiMaxNode(Set[AttributeName](),Map[AttributeName,mutable.Set[JsonExplorerType]](),0,attributeMap.map(x => (Map[AttributeName,mutable.Set[JsonExplorerType]]((x._1,x._2._1)),x._2._2)).toList.to[mutable.ListBuffer])
                )), false // flatten non-root
              )

          case Right(r) =>
            (x._1,
              mutable.Seq(mutable.Seq(
                BiMaxNode(Set[AttributeName](),Map[AttributeName,mutable.Set[JsonExplorerType]](),0,r.map(x => (Map[AttributeName,mutable.Set[JsonExplorerType]]((x._1,x._2._1)),x._2._2)).toList.to[mutable.ListBuffer])
              )), false // flatten var_objects
            )
        }

      })
        .map(x => if (x._3) (x._1,Exec.Algorithms.runKMeans(config.spark.sparkContext,x._2,10)) else (x._1,x._2)).toMap

      //TODO track basic types from raw schemas

      // combine subset types for each attribute
      val mergedSchemas:  Map[AttributeName,DisjointNodes] = rawSchemas.map{case(name,djn) => (name,djn.map(bms => bms.map(NodeToJsonSchema.biMaxNodeTypeMerger(_))))}

      val variableObjWithMult: Map[AttributeName,(mutable.Set[JsonExplorerType],Int)] = variableObjs
        .map(varObjName => {val m = mergedSchemas
          .map(djn => { val d = djn._2
            .flatMap(possibleSchemas => possibleSchemas
              .map(z => {
                val first = if (z.multiplicity > 0) z.types.get(varObjName) match {case Some(v) => (v,z.multiplicity) case None => (mutable.Set[JsonExplorerType](),0)} else (mutable.Set[JsonExplorerType](),0)
                val sec = if(z.subsets.nonEmpty) z.subsets.map(sub => if (sub._1.contains(varObjName)) (sub._1.get(varObjName).get,sub._2) else (mutable.Set[JsonExplorerType](),0)).reduce((l:(mutable.Set[JsonExplorerType],Int),r:(mutable.Set[JsonExplorerType],Int)) => (l._1 ++ r._1, l._2 + r._2))
                else (mutable.Set[JsonExplorerType](),0)
                (first._1 ++ sec._1,first._2+sec._2)
              })
            )
            d
          })

          (varObjName,m.flatten.reduce((l,r) => (l._1 ++ r._1, l._2 + r._2)))
        }).toMap


      def reduceTypes(s: mutable.Set[JsonExplorerType]): mutable.Set[JsonExplorerType] = {
        if(s.size == 1)
          return s
        val typesWithoutEmpty = s.filter( t => if (t.equals(JE_Empty_Object) && s.contains(JE_Object) || (t.equals(JE_Empty_Array) && s.contains(JE_Array))) false else true)
        val types = typesWithoutEmpty.filter( t => if (t.equals(JE_Null) && typesWithoutEmpty.size == 2) false else true)
        return types
      }

      val reducedMergedSchemas = mergedSchemas.map(x => (x._1,x._2.map(y => y.map(z => {
        BiMaxNode(z.schema,
          z.types.map(r => (r._1, reduceTypes(r._2))),
          z.multiplicity,
          z.subsets
        )

      }))))
      //util.JsonSchemaToJsonTable.convert(reducedMergedSchemas, variableObjs, objArrs)
      val JsonSchema: util.JsonSchema.JSS = util.NodeToJsonSchema.biMaxToJsonSchema(mergedSchemas,variableObjWithMult, objArrs)
      algorithmSchema = JsonSchema.toString  + "\n"
    } else {
      throw new Exception("Unknown Merge algorithm choice")
    }


    val endTime = System.currentTimeMillis() // End Timer


    //log += LogOutput("FVTime",fvRunTime.toString,"FV Creation Took: "," ms")
    Log.add("total time",(endTime - startTime).toString)
    Log.add("train percent",config.trainPercent.toString)
    Log.add("validation size",config.validationSize.toString)
    Log.add("algorithm",config.runBiMax.toString())
    Log.add("seed",config.seed match {
      case Some(i) => i.toString
      case None => "None"})

    config.spark.conf.getAll.foreach{case(k,v) => Log.add(k,v)}
    Log.add("KSE",config.kse.toString)

//    println(SizeEstimator.estimate(featureVectors.filter(x=> x._1.isEmpty || attributeMap.get(x._1).get.`type`.contains(JE_Var_Object))))
//    println(SizeEstimator.estimate(featureVectors))

    Log.writeLog(config.logFileName, if(config.writeJsonSchema) algorithmSchema else "")
    Log.printLog()

  }

}

// Row Counts:
// Medicine: 239,930
// Github: 3,321,596
// Yelp: 7,437,120
//  - Business: 156,639
//  - Checkin: 135,148
//  - Photos: 196,278
//  - Review: 4,736,897
//  - Tip: 1,028,802
//  - User: 1,183,362
// Synapse: 147847
// Twitter: 808,442
// NYT2019: 69116
// WikiData: 16980683 -- 1700614
//            1700614