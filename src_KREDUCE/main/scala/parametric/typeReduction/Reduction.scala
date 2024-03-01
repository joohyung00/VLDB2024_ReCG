package parametric.typeReduction

import parametric.typeDefinition._

import org.slf4j.LoggerFactory

@SerialVersionUID(100L)
class Reduction extends Serializable{
  val logger = LoggerFactory.getLogger(classOf[Reduction])


  def Reduce(T1:countingType, T2:countingType, equiv:(structuralType,structuralType)=>Int):countingType = (T1,T2) match {
    case (Empty(), _) => T2
    case (_, Empty()) => T1

    case (u1:unionType, u2:unionType) => unionType(stuctTypeListFuse(u1.body,u2.body,equiv))

    case (s1:structuralType,s2:structuralType) =>  equiv(s1,s2) match {
      case 0 => Fuse(s1,s2,equiv)
      case _ => unionType(List(s1,s2).sortWith(equiv(_,_)<0))
    }

    case (u1:unionType,s2:structuralType) => unionType(stuctTypeListFuse(u1.body,List(s2),equiv))
    case (s1:structuralType,u2:unionType) => unionType(stuctTypeListFuse(List(s1),u2.body,equiv))

  }
    /*fuse list of structural types*/
  def stuctTypeListFuse(L1:List[structuralType], L2:List[structuralType], equiv:(structuralType,structuralType)=>Int):List[structuralType]=(L1,L2) match {
    case (List(), List()) => List()
    case (L1, List()) => L1
    case (List(), L2) => L2
    case (hl1::tl1, hl2::tl2) =>{
      val v = equiv(hl1,hl2)
      if(v<0) hl1::stuctTypeListFuse(tl1,L2,equiv)
      else if(v>0) hl2::stuctTypeListFuse(L1,tl2,equiv)
      else Fuse(hl1,hl2,equiv)::stuctTypeListFuse(tl1,tl2,equiv)
    }
  }


  def Fuse(S1:structuralType, S2:structuralType, equiv:(structuralType,structuralType)=>Int):structuralType = (S1,S2) match {

    /*Basic types*/
    case (Null(m),Null(n)) => Null(m+n)
    case (Bool(m),Bool(n)) => Bool(m+n)
    case (Numb(m),Numb(n)) => Numb(m+n)
    case (Str(m),Str(n)) => Str(m+n)

    /*Record types*/
    case (RecordType(fl1,m),RecordType(fl2,n))=> RecordType(ftypeListFuse(fl1,fl2,equiv),m+n)

    /*Array types*/
    case (ArrayType(t1,m),ArrayType(t2,n)) => ArrayType(Reduce(t1,t2,equiv),m+n)

  }

  /*fuse list of type fields*/
  def ftypeListFuse(L1:List[fieldType], L2:List[fieldType], equiv:(structuralType,structuralType)=>Int):List[fieldType] = (L1,L2) match {
    case (List(), List()) => List()
    case (fl1, List()) => fl1
    case (List(), fl2) => fl2
    case (h1::t1,h2::t2) => {
      val v = h1.compare(h2)
      if(v<0) h1::ftypeListFuse(t1,L2,equiv)
      else if(v>0) h2::ftypeListFuse(L1,t2,equiv)
      else new fieldType(h1.getLabel(),Reduce(h1.getBody(),h2.getBody(),equiv)) ::ftypeListFuse(t1,t2,equiv)
    }
  }
}