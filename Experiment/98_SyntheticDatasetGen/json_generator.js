// Default libraries
const fs = require('fs');
const {array} = require('yargs');
const {writeFile} = require('fs');

// Dependent libraries
const yargs = require('yargs');
const jsf = require('json-schema-faker');


const argv = yargs
  .option('in_path', {
    description: 'Path to the schema file',
    type: 'string'
  })
  .option('out_path', {
    description: 'Path to return the JSON data file',
    type: 'string'
  })
  .option('num', {
    description: 'Num of JSON data to generate',
    type: 'number'
  })
  .help()
  .alias('help', 'h').argv;


// Load JSON schema file
let rawfile = fs.readFileSync(argv.in_path);
let schema = JSON.parse(rawfile);


// Generate JSON documents
let generated_docs = [];

console.log(argv.num)

for(let i = 0; i < argv.num; i++)
{
  generated_docs.push(JSON.stringify(jsf.generate(schema)));
}

// Output file
for(let i = 0; i < argv.num; i++)
{
  fs.appendFile(argv.out_path, generated_docs[i] + '\n', (err) => {if (err) ; else ;})
}

console.log("FIN")
