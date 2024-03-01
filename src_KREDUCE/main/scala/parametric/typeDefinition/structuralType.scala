package parametric.typeDefinition

import play.api.libs.json._

@SerialVersionUID(100L)
sealed class structuralType(val card: Long) extends countingType with Serializable {
   def isEqualTo(other: structuralType): Boolean = (this,other) match {
     case (l:Null,r:Null) => this.card==other.card
     case (l:Numb,r:Numb) => this.card==other.card
     case (l:Bool,r:Bool) => this.card==other.card
     case (l:Str,r:Str) => this.card==other.card
     case (l:RecordType,r:RecordType) => l.isEqualTo(r)
     case (l:ArrayType,r:ArrayType) => l.isEqualTo(r)
     case (_,_) => false
  }//useful for tests



  val _fieldSep   = ", "
  val _kindSep = 1
  val helper = new Helper()

  val rEmpty = 1
  val rNull = rEmpty+ _kindSep
  val rBool = rNull+ _kindSep
  val rNumb = rBool+ _kindSep
  val rStr = rNumb+ _kindSep
  val maxBase = rStr
  val rRecord = maxBase+ _kindSep
  val rArray = rRecord+ _kindSep

  val tNull = "NullType"
  val tBool = "BoolType"
  val tNumb = "NumType"
  val tStr = "StrType"
  val tRec = "Record"
  val tArr = "Array"


  def kind():Int= this match
  {

    case Null(_)=>rNull
    case Bool(_)=>rBool
    case Numb(_)=>rNumb
    case Str(_)=>rStr
    case RecordType(_,_)=>rRecord
    case ArrayType(_,_)=>rArray
  }


  def kindOrdering(other: structuralType)= this.kind()-other.kind()

  /**assumes records with sorted keys*/
  def labelOrdering(other: structuralType)= (this,other) match{
    case (r1:RecordType,r2:RecordType) => helper.strListCompare(r1.labels(),r2.labels())
    case (_,_) => this.kindOrdering(other)
  }

  /*TODO deep-value ordering*/

  override def getCardinality()=card

}

/*Basic types*/
//case class Empty(override val card: Long) extends structuralType(card)
case class Null(override val card: Long) extends structuralType(card){
  override def toString: String = tNull

}
case class Bool(override val card: Long) extends structuralType(card){
  override def toString: String = tBool

}
case class Numb(override val card: Long) extends structuralType(card){
  override def toString: String = tNumb
}
case class Str(override val card: Long) extends structuralType(card){
  override def toString: String = tStr
}

/*Record types*/
case class RecordType(body: List[fieldType], override val card: Long) extends structuralType(card){
  def labels():List[String]=body.map(_.getLabel())
  override def toString: String = tRec

  /*l and r sorted*/
  def deepEqual(l: List[fieldType], r: List[fieldType]): Boolean  = (l,r) match {
    case (Nil,Nil) => true
    case (h1::t1, h2::t2) => h1.isEqualTo(h2) && deepEqual(t1,t2)
    case _ => false
  }
   def isEqualTo(other: RecordType): Boolean =
     other.card==this.card && other.body.size==this.body.size &&
      other.labels()==this.labels() && deepEqual(other.body,this.body)
}

/*Array types*/
case class ArrayType(body:countingType, override val card: Long)extends structuralType(card){
  override def toString: String = tArr

  def isEqualTo(other: ArrayType): Boolean = (other.card==this.card) && this.body.isEqualTo(other.body)

}