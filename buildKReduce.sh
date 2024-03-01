
mv src src_JXPLAIN
mv src_KREDUCE src
mv build.sbt build_JXPLAIN.txt
mv build_KREDUCE.txt build.sbt
mv target target_JXPLAIN
mv target_KREDUCE target

sbt assembly

mv target target_KREDUCE
mv target_JXPLAIN target
mv build.sbt build_KREDUCE.txt
mv build_JXPLAIN.txt build.sbt
mv src src_KREDUCE
mv src_JXPLAIN src