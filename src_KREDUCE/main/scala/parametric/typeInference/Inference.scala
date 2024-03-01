package parametric.typeInference

import parametric.typeDefinition._
import org.slf4j.LoggerFactory
import play.api.libs.json._

@SerialVersionUID(100L)
class Inference extends  Serializable{
  val logger = LoggerFactory.getLogger(classOf[Inference])


  def inferStructType(parsed: JsValue,
                      f: (countingType, countingType, (structuralType,structuralType)=>Int) => countingType,
                      order:(structuralType,structuralType)=>Int):structuralType = parsed match {
    case JsNull => Null(1)
    case boolean: JsBoolean => Bool(1)
    case JsNumber(_) => Numb(1)
    case JsString(_) => Str(1)
    case JsArray(value) => ArrayType(value.map(inferStructType(_,f,order)).fold(Empty())((T1,T2)=> f(T1,T2,order)),1)
    case JsObject(underlying) => RecordType(underlying.map{case (k,v) => new fieldType(k,inferStructType(v,f,order))}.toList.sorted,1)
  }

//  def inferStructType(json: JSValue,
//                      f: (countingType, countingType, (structuralType,structuralType)=>Int) => countingType,
//                      order:(structuralType,structuralType)=>Int):structuralType = json match {
////    case JNothing => Empty() //1 is just arbitrary
//    case JNull => Null(1)
//    case JBool(x) => Bool(1)
//    case JInt(x) => Numb(1)
//    case JDecimal(x) => Numb(1)
//    case JDouble(x) => Numb(1)
//    case JString(x) => Str(1)
//    case JObject(flist) => RecordType(flist.map(paire =>new fieldType(paire._1,inferStructType(paire._2, f, order))).sorted,1)
//    case JArray(vlist) => {
//      val tlist = vlist.map(inferStructType(_,f,order).asInstanceOf[countingType]) /*typecast required to match signatures*/
//      ArrayType(tlist.fold(Empty())((T1,T2)=> f(T1,T2,order)),1)
//    }
//  }

}
