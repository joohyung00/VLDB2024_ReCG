// Default libraries
const { array } = require('yargs')
const { writeFile } = require('fs')

// Dependent libraries
const yargs = require('yargs')
const jsf = require('json-schema-faker')

const Ajv = require('ajv')
const { errorMonitor } = require('events')
const ajv = new Ajv()

const Validator = require('jsonschema').Validator
const v = new Validator()













const argv = yargs
	.option('goal_schema_path', {
		description: 'Path to the goal schema file',
		type: 'string',
		demandOption: true
	})
	.option('negative_schema_path', {
		description: "Path to the negative schema file",
		type: "string",
		demandOption: true
	})
	.option('operation', {
		description: "",
		type: "string",
		demandOption: true
	})
	.option('nesting_level', {
		description: "",
		type: "string",
		demandOption: true
	})
	.option('path', {
		description: "",
		type: "string",
		demandOption: true
	})
	.option('temp', {
		description: 'Path to return the JSON data file',
		type: 'string',
		demandOption: true
	})
	.help()
	.alias('help', 'h').argv





function appendJSONSync(filename, data) 
{
	try 
	{
		if (fs.existsSync(filename)) 
		{
			fs.appendFileSync(filename, "\n" + JSON.stringify(data));
		}
		else 
		{
			fs.writeFileSync(filename, JSON.stringify(data));
		}
	}
	catch (err)
	{
		console.error(`Error appending JSON to file: ${err}`);
	}
}

const fs = require('fs');

let goal_schema;

try 
{ goal_schema = JSON.parse(fs.readFileSync(argv.goal_schema_path, 'utf8')); } 
catch (error) 
{ console.error('Error reading or parsing JSON:', error); }

let negative_schema;

try 
{ negative_schema = JSON.parse(fs.readFileSync(argv.negative_schema_path, 'utf8')); } 
catch (error) 
{ console.error('Error reading or parsing JSON:', error); }

let operations;
try
{ operations = JSON.parse(argv.operation); }
catch (error)
{ console.error('Error reading or parsing JSON:', error); }

const TRIALS = 30
var trials = 0
// Generate JSON documents

while (trials < TRIALS) {
	let generated_json;

	if (operations.includes("anyOf_object_tuple_collection")) 
	{
		let collection_part = {};
		let tuple_part = {};

		for (const key in negative_schema) 
		{
			if (key === 'additionalProperties') {
				collection_part[key] = negative_schema[key];
				collection_part["type"] = "object";
			} 
			else 
			{
				tuple_part[key] = negative_schema[key];
			}
		}
		tuple_part["additionalProperties"] = false;

		let generated_1 = jsf.generate(collection_part);
		let generated_2 = jsf.generate(tuple_part);

		generated_json = {...generated_1, ...generated_2}
	}
	else
	{
		generated_json = jsf.generate(negative_schema)
	}

	if (v.validate(generated_json, goal_schema).valid == false) 
	{
		var neg_sample = {}
		neg_sample["operation"] = JSON.parse(argv.operation)
		neg_sample["data"] = generated_json
		neg_sample["path"] = JSON.parse(argv.path)
		neg_sample["nesting_level"] = JSON.parse(argv.nesting_level)

		appendJSONSync(argv.temp, neg_sample)
		break
	}
	else 
	{
		trials += 1
	}
}

if (trials == TRIALS) 
{
	appendJSONSync(argv.temp, ["FAILED", argv.operation, argv.path])
}