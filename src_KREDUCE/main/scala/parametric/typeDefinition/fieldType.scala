package parametric.typeDefinition

@SerialVersionUID(100L)
class fieldType(label:String, body:countingType) extends Ordered[fieldType] with Serializable {
  /**
    * setters and getters
    */
  def getCardinality() = body.getCardinality()
  override def toString()= this.getClass.getName+"("+this.label+","+ this.body.toString+")"
  def getLabel()=this.label
  def getBody()=this.body
  def compare(other: fieldType) = this.label.compareTo(other.getLabel())
  def isEqualTo(other: fieldType) = (this.compare(other)==0) && body.isEqualTo(body)
}
