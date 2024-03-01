var express = require('express');
var router = express.Router();

const dslParser = require('../grammars/dsl/parser')
const jsonParser = require('../grammars/json_schema/parser/parser')

const dslConverter = require('../grammars/dsl/conversions')
const jsonConverter = require('../grammars/json_schema/converter/converter')

const { resolve_refs } = require('../grammars/json_schema/converter/refs')
const { translateMsg } = require('../utils/utils')

const ws = "‏‏‎ ‎"
const settings_str = `"settings": {\n${ws}${ws}"datagen_language": ?,\n${ws}${ws}"recursion": {"lower": ?, "upper": ?},\n${ws}${ws}"prob_if": ?,\n${ws}${ws}"prob_patternProperty": ?,\n${ws}${ws}"random_props": ?,\n${ws}${ws}"extend_objectProperties": ?,\n${ws}${ws}"prefixItems": ?,\n${ws}${ws}"extend_schemaProperties": ?\n}`
const isObject = x => typeof x == 'object' && !Array.isArray(x) && x !== null

// Default libraries
const fs = require('fs')
const { array } = require('yargs')
const { writeFile } = require('fs')

// Dependent libraries
const yargs = require('yargs')

const Ajv = require('ajv')
const { errorMonitor } = require('events')
const ajv = new Ajv()

const Validator = require('jsonschema').Validator
const v = new Validator()


// function cleanSettings(settings, frontend) {
//   if (frontend) {
//     settings.recursion.lower = parseInt(settings.recursion.lower)
//     settings.recursion.upper = parseInt(settings.recursion.upper)
//     settings.prob_if = parseFloat(settings.prob_if)
//   }

//   if (!(Number.isInteger(settings.recursion.lower) && settings.recursion.lower >= 0)) return "O valor 'recursion.lower' das definições deve ser um inteiro não-negativo!"
//   if (!(Number.isInteger(settings.recursion.upper) && settings.recursion.upper >= 0)) return "O valor 'recursion.upper' das definições deve ser um inteiro não-negativo!"
//   if (settings.recursion.upper < settings.recursion.lower) return "O valor 'recursion.lower' deve ser inferior ou igual ao 'recursion.upper'!"
//   if (!(typeof settings.prob_if == "number" && settings.prob_if >= 0 && settings.prob_if <= 100)) return "O valor 'prob_if' das definições deve ser um número entre 0 e 100, correspondente à probabilidade pretendida!"
//   if (!(typeof settings.prob_patternProperty == "number" && settings.prob_patternProperty >= 0 && settings.prob_patternProperty <= 100)) return "O valor 'prob_patternProperty' das definições deve ser um número entre 0 e 100, correspondente à probabilidade pretendida!"
//   if (!typeof settings.random_props == "boolean") return "O valor 'random_props' das definições deve ser um boleano!"
//   if (!(typeof settings.datagen_language == "string" && ["pt","en"].includes(settings.datagen_language))) return `O valor 'datagen_language' das definições deve ter um dos seguintes valores: "pt" (português) ou "en" (inglês)!`

//   if (!frontend) {
//     if (!(typeof settings.extend_objectProperties == "string" && ["extend","overwrite"].includes(settings.extend_objectProperties))) return "O valor 'extend_objectProperties' das definições, relativo à extensão de propriedades repetidas nas chaves 'properties' e 'patternProperties', deve ser uma das seguintes strings:\n\n• extend/overwrite - se as chaves tiverem propriedades repetidas, estende/subtitui a schema de cada propriedade da chave-base com a respetiva schema da mesma propriedade da chave nova. Todas as propriedades originais da nova chave são atribuídas à chave-base."
//     if (!(typeof settings.extend_schemaProperties == "string" && ["extend","overwrite"].includes(settings.extend_schemaProperties))) return "O valor 'extend_schemaProperties' das definições, relativo à extensão de chaves cujo valor é uma subschema ('propertyNames', 'additionalProperties', 'unevaluatedProperties', 'items' ou 'unevaluatedItems'), deve ser uma das seguintes strings:\n\n• extend/overwrite - estende/substitui a schema da chave-base com a schema da chave nova."
//     if (!(typeof settings.extend_prefixItems == "string" && ["extend","partial_overwrite","total_overwrite","append"].includes(settings.extend_prefixItems))) return "O valor 'extend_prefixItems' das definições, relativo à extensão da chave 'prefixItems', deve ser uma das seguintes strings:\n\n• extend - para todas as schemas que se encontram no mesmo índice, estende as da chave-base com as respetivas schemas da nova chave. Se a chave nova tiver mais elementos do que a base, os elementos extra são também concatenados;\n• append - os elementos do novo 'prefixItems' são concatenados aos da chave-base;\n• partial_overwrite - sobrescreve apenas as schemas da chave-base com uma schema correspondente no mesmo índice, na chave nova. Se a chave nova tiver mais elementos do que a base, os elementos extra são também concatenados;\n• total_overwrite - o valor da chave-base é apagado totalmente e substítuido pelo array do novo 'prefixItems'."

//     settings.extend_objectProperties = settings.extend_objectProperties == "extend" ? "OR" : "OW"
//     settings.extend_schemaProperties = settings.extend_schemaProperties == "extend" ? "OR" : "OW"
//     settings.extend_prefixItems = settings.extend_prefixItems == "extend" ? "OR" : (settings.extend_prefixItems == "append" ? "AP" : (settings.extend_prefixItems == "partial_overwrite" ? "OWP" : "OWT"))
//   }

//   settings.prob_if = parseFloat(settings.prob_if.toFixed(2))/100
//   settings.prob_patternProperty = parseFloat(parseFloat(settings.prob_patternProperty).toFixed(2))/100

//   return true
// }

// POST front-end para gerar um dataset a partir de uma schema JSON
// router.post('/', (req, res) => {
//   let schema_key = ""

//   try {
//     // extrair dados da schema
//     let data = req.body.schemas.map(x => {schema_key = x.key; return jsonParser.parse(x.content)})
//     console.log('schema parsed')

//     res.status(201).jsonp(generate(req, data, true))
//   } catch (err) {
//     res.status(201).jsonp({...err, schema_key})
//   }
// });

// // POST back-end para gerar um dataset a partir de uma schema JSON
// router.post('/:output', (req, res) => {
//   if (req.params.output != "xml" && req.params.output != "json") return res.sendStatus(404)

//   if (Object.keys(req.body).length == 3 && "main_schema" in req.body && "other_schemas" in req.body && "settings" in req.body) {
//     req.body.settings.output = req.params.output
//     let settings = req.body.settings

//     if (!isObject(req.body.main_schema)) return res.status(500).send("A schema principal deve ser enviada em forma de objeto JSON!")
//     if (!(Array.isArray(req.body.other_schemas) && req.body.other_schemas.every(x => isObject(x)))) return res.status(500).send("O valor de 'other_schemas' deve ser um array com as restantes schemas, todas elas em forma de objeto JSON!")

//     if (!(typeof settings == 'object' && !Array.isArray(settings) && settings !== null && "recursion" in settings && "lower" in settings.recursion && "upper" in settings.recursion && "prob_if" in settings && "prob_patternProperty" in settings && "random_props" in settings && "extend_objectProperties" in settings && "extend_prefixItems" in settings && "extend_schemaProperties" in settings && "datagen_language" in settings))
//       return res.status(500).send(`As definições enviadas no pedido não estão corretas! Devem ser enviadas num objeto com a seguinte estrutura:\n\n${settings_str}`)

//     let schema_key = ""
//     let schemas = [JSON.stringify(req.body.main_schema, null, 2), ...req.body.other_schemas.map(x => JSON.stringify(x, null, 2))]
//     try {
//       // extrair dados da schema
//       let data = schemas.map((x,i) => {schema_key = i; return jsonParser.parse(x)})
//       console.log('schema parsed')

//       let result = generate(req, data, false)
//       if ("message" in result) return res.status(500).send(result.message)
//       res.status(201).jsonp(result)
//     } catch (err) {
//       res.status(500).send(`Erro na ${!schema_key ? "schema principal" : `${schema_key}º schema das restantes`}:\n` + translateMsg(err, schemas[schema_key]))
//     }
//   }
//   else res.status(500).send(`O corpo do pedido deve ter apenas três propriedades: 'main_schema', 'other_schemas' e 'settings'.\nAs definições devem ser enviadas num objeto com a seguinte estrutura:\n\n${settings_str}`)
// });




function generate(schema) {
    let settings = {
        "recursion": { "lower": 1, "upper": 3 },
        "prob_if": 50,
        "datagen_language": "en"
    }

    // let clean = cleanSettings(req.body.settings, frontend)
    // if (typeof clean == "string") return {message: clean}

    let datum = [{ "key": 1, "content": schema }]

    let data = datum.map(x => {
        schema_key = x.key;
        return jsonParser.parse(x.content)
    })
    // console.log('schema parsed')
    // let settings = {"recursion": 5}

    // let resolved = resolve_refs(data, req.body.settings)
    let resolved = resolve_refs(data, settings)
    if (resolved !== true) return { message: resolved }


    // criar modelo DSL a partir dos dados da schemas
    // let model = jsonConverter.convert(data[0], req.body.settings)
    let model = jsonConverter.convert(data[0], settings)
    // console.log('modelo criado')

    // gerar dataset
    let dataset = dslParser.parse(model)
    // let format = req.body.settings.output
    // console.log('dataset gerado')

    // converter dataset para o formato final
    // if (format == "json") 
    dataset = JSON.parse(JSON.stringify(dslConverter.cleanJson(dataset.dataModel.data), null, 2))

    // if (format == "xml") {
    //   let schema = data[0].subschemas.pop()
    //   dataset = dslConverter.jsonToXml(dataset.dataModel.data, {root_name: /^anon\d+$/.test(schema.id) ? "dataset" : schema.id.split("/schemas/")[1]})
    // }
    //console.log('dataset convertido')

    // console.log(dataset)

    return dataset
}

const argv = yargs
    .option('mode', {
        type: 'string'
    })
    .option('num', {
        type: 'number'
    })
    .option('goal_schema_path', {
        type: 'string'
    })
    .option('negative_schema_path', {
        type: "string"
    })
    .option('operation', {
        type: "string"
    })
    .option('nesting_level', {
        type: "string"
    })
    .option('path', {
        type: "string"
    })
    .option('temp', {
        type: 'string'
    })
    .help()
    .alias('help', 'h').argv


function appendJSONSync(filename, data) {
    try {
        if (fs.existsSync(filename)) {
            fs.appendFileSync(filename, "\n" + JSON.stringify(data));
        } else {
            fs.writeFileSync(filename, JSON.stringify(data));
        }
    } catch (err) {
        console.error(`Error appending JSON to file: ${err}`);
    }
}


if (argv.mode == "positive") 
{
    console.log(argv.num)

    let goal_schema;
    try {
        // goal_schema = JSON.parse(fs.readFileSync(argv.goal_schema_path, 'utf8'));
        goal_schema = fs.readFileSync(argv.goal_schema_path, 'utf8');
    }
    catch (error) {
        console.error('Error reading or parsing JSON:', error);
    }
    
    // Output file
    for(let i = 0; i < argv.num; i++)
    {
        var generated_json = generate(goal_schema)
        appendJSONSync(argv.path, generated_json)
    }
    
    console.log("FIN")
    
}
else if (argv.mode == "negative") {
    // Load JSON schema file
    let goal_schema;
    let parsed_goal_schema;
    try 
    {
        goal_schema = fs.readFileSync(argv.goal_schema_path, 'utf8');
        parsed_goal_schema = JSON.parse(fs.readFileSync(argv.goal_schema_path, 'utf8'));
    }
    catch (error) 
    {
        console.error('Error reading or parsing JSON:', error);
    }

    let negative_schema;
    let parsed_negative_schema;
    try 
    { 
        negative_schema = fs.readFileSync(argv.negative_schema_path, 'utf8'); 
    }
    catch (error) { console.error('Error reading or parsing JSON:', error); }

    const TRIALS = 30
    var trials = 0
    // Generate JSON documents

    while (trials < TRIALS) {
        var generated_json = generate(negative_schema)

        if (v.validate(generated_json, parsed_goal_schema).valid == false) {
            var neg_sample = {}
            neg_sample["operation"] = argv.operation
            neg_sample["data"] = generated_json
            neg_sample["path"] = argv.path
            neg_sample["nesting_level"] = argv.nesting_level

            appendJSONSync(argv.temp, neg_sample)
            break
        }
        else {
            trials += 1
        }
    }

    if (trials == TRIALS) {
        appendJSONSync(argv.temp, ["FAILED", argv.operation])
    }
}