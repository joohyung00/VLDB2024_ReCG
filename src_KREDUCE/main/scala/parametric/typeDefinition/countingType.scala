package parametric.typeDefinition


@SerialVersionUID(100L)
class countingType() extends Serializable {
  def getCardinality():Long = this match {
    case t:unionType=>t.getCardinality()
    case t:Empty => 0
  }
  def isEqualTo(other: countingType): Boolean = (this,other) match {
    case (l:unionType, r:unionType )=> l.isEqualTo(r)
    case (l:structuralType, r:structuralType) => l.isEqualTo(r)
    case (l:Empty,r:Empty) => true
    case (_,_) => false
  }
}
case class unionType(body: List[structuralType]) extends countingType {
  override def toString: String = "Union"
  override def getCardinality(): Long = body.map(s=>s.getCardinality).sum

  /*l and r sorted*/
  def deepEqual(l: List[structuralType], r: List[structuralType]): Boolean  = (l,r) match {
    case (Nil,Nil) => true
    case (h1::t1, h2::t2) => h1.isEqualTo(h2) && deepEqual(t1,t2)
    case _ => false
  }

  def isEqualTo(other: unionType): Boolean =  other.getCardinality==this.getCardinality && other.body.size==this.body.size &&
    deepEqual(this.body,other.body)

//  override def equals(other: countingType): Boolean =
}
case class Empty() extends countingType {
  override def getCardinality(): Long = 0
  override def toString: String = "EmptyType"

}


/**/