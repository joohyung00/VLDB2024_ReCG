package parametric.typeDefinition

import parametric.descStats
import play.api.libs.json
import play.api.libs.json._
import scala.util.Random._

@SerialVersionUID(100L)
class Formatter extends Serializable {
  //cardinalities
  val _card = "__Card"
  val _proba = "__Proba"
  val _amin = "__MinSize"
  val _amax = "__MaxSize"
  val _lmin = "__MinLength"
  val _lmax = "__MaxLength"
  val _vmin = "__MinVal"
  val _vmax = "__MaxVal"
  val _trues = "__trues"
  val _falses ="__falses"

  //Metanames
  val _kind = "__Kind"
  val _content = "__Content"
  val _equiv = "__Equiv"
  val _optional = "__Optional"

  //Metadata
  val _stats="stats"
  val _metadata = "metadata"
  val _schema = "schema"
//  val _timestamp = "timestamp"
//  val _hdfspath = "hdfspath"
  val _execTime= "execTime"
//  val _nbObjects = "nbObjects"

  val _defaultOptLen = 10

  /**
    *
    * @param input
    * @param counting
    * @return
    *         TODO implement counting
    */
//  def jsonToFinalStr(input : countingType, counting: Boolean, equivLabel: String) : String = {
//    pretty(render(typeToJson(input,equivLabel)))
//  }

  def typeAndMDToJson(input: countingType, equivLabel: String, statList: List[descStats]): JsValue = {
  val content: Map[String, JsValue] = statList.map(s=>(s.label,s.toJson())).toMap
  JsObject(Map(_schema->typeToJson(input), _stats->JsObject(content)))
}

  def typeToJsonMD(input: countingType, execTime: Long, stats: Map[String,String]):JsObject = {
    val jsStats = stats.map{case(lab,num)=>(lab->JsString(num))}++Map(_execTime->JsNumber(execTime))
    val content: Map[String, JsValue] = Map(_schema->typeToJson(input), _metadata->JsObject(jsStats))
    JsObject(content)
  }



   /**
    *
    * @param input
    * @return
    */
  def typeToJson(input: countingType): JsObject = {
    input match {
      case Empty()|Null(_)|Bool(_)|Numb(_)|Str(_) =>  new JsObject(Map(_kind->JsString(input.toString())))

      case RecordType(body,card) => {
        var res = Map[String, JsValue]()
        res += (_content->JsObject(body.map(field => fieldTypeSer(field, card))))
        res += (_kind->JsString(input.toString()))
        JsObject(res)
      }
      case ArrayType(body,_) =>{
        var res = Map[String, JsValue]()
        res += (_content->typeToJson(body))
        res += (_kind -> JsString(input.toString()))
        JsObject(res)
      }
      case unionType(body) => {
        var res = Map[String, JsValue]()
        res += (_content-> JsArray(body.map(t=>typeToJson(t))))
//        res += (_equiv-> JsString(input.toString()))
        res += (_kind-> JsString(input.toString()) )
        JsObject(res)
      }
    }
  }

//  type field = (String,JsValue)

  /**
    * potentially creates non-unique key-value pairs
    * @param field
    * @param equivLabel
    * @param card
    * @return
    */
  def fieldTypeSerOld(field: fieldType, equivLabel: String, card: Long) = {
    var m = Map[String, JsValue]()
    val result = (field.getLabel()->typeToJson(field.getBody()))
    m += result
    if ((equivLabel=="k" || equivLabel=="K") && field.getBody().getCardinality()<card)
      (_optional->JsObject(m))
    else result
  }

  /**
    * optional fields are associated with a record containing a field _optional: true
    * mandatory fields do not contain such a field
    * @param field
    * @param equivLabel
    * @param card
    * @return
    */

  def randsuffix(len: Integer)=alphanumeric.take(len).mkString
  def formatOptional(len: Integer)= _optional+"_"+randsuffix(len)

  def fieldTypeSer(field: fieldType, card: Long): (String, JsValue) = {
    val label = field.getLabel()
    val content = typeToJson(field.getBody())

    if (field.getBody().getCardinality() < card)
      (label -> new JsObject(List(formatOptional(_defaultOptLen)->content).toMap))
    else
      (label -> content)
  }


}
