package parametric
import play.api.libs.json._


 class descStats(val label: String, var min: BigInt, var max: BigInt, var sum: BigInt, var count: BigInt) {
  val _min = "min"
  val _max = "max"
  val _avg = "avg"

  def get() = Map(_min->min, _max->max,_avg->sum/count)
  def update(v:BigInt) = {
    if (v < min) min = v;
    if (v > max) max = v;
    sum += v
    count+=1
  }

  /**
   * ouptut an object {label: {min, max, avg}}
   * @return
   */
  def toJson() = JsObject(Map(label->Json.toJson(this.get())))
}