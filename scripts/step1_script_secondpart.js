// FUENTE: elaboracion propia

//Con este script se obtienen los puntos de los boundingBoxes impresos en la consola.
//Luego se procede a copiar estos puntos ordenados en un archivo .txt para que entre
//en el modelo YOLOv4 personalizado.

'use strict'

//Se cargan las librerias y dependencias que se usarán
const fs = require('fs');
var parser = require('xml2json');

//Se hace un bucle para llamar a cada arhivo .XML creado por LabelImg
for (var i = 1; i < 647; i++) {

//Se definen los directorios de los archivos .XML y las imágenes
  var path = './'+i+'.xml';
  var pat1 = './'+i+'.JPEG';
  var pat2 = './'+i+'.jpg';
  var pat3 = './'+i+'.PNG'

//Se verifica la existencia de los archivos en los directorios definidos
  var img = '.';
  if (fs.existsSync(pat1)) {
    img += 'JPEG';
  }else if (fs.existsSync(pat2)) {
    img += 'jpg';
  }else if (fs.existsSync(pat3)) {
    img += 'PNG';
  }

//Se lee la data de los archivos .XML y se guarda en una variable llamada 'data'
  var data = fs.readFileSync(path);
  var json = parser.toJson(data);
  var inne = JSON.parse(json);
  var objA = inne["annotation"]["object"];    //Se buscan los objetos(boundingBoxes) creados
                                              //con LabelImg

//En esta variable se guardara el nombre de la imagen con las coordenadas de los BBoxes
  var final = i+img;

//Si no existe el arreglo de boundingBoxes, o sea solo hay un BBox, se entra en esta condición
  if (objA[0] == undefined) {

//Se definen variables donde se almacenan los x e y de los puntos creados por LabelImg
        var bndb = objA["bndbox"];
        var _xmi = bndb["xmin"];
        var _ymi = bndb["ymin"];
        var _xma = bndb["xmax"];
        var _yma = bndb["ymax"];

//Se lee si estos bounding boxes corresponden a una persona con mascara o sin mascara
        var mask = 0;
        if (objA["name"] == 0) {
            mask = 0;
        }else {
            mask = 1;
        }

        final += ' '+_xmi+','+_ymi+','+_xma+','+_yma+','+mask;

//Si hay mas de un BBox, el arreglo se creara y entrara en esta condición
      }else {
              objA.forEach((item, j) => {
                    var bndb = item["bndbox"];
                    var _xmi = bndb["xmin"];
                    var _ymi = bndb["ymin"];
                    var _xma = bndb["xmax"];
                    var _yma = bndb["ymax"];


                    var mask = 0;
                    if (item["name"] == 0) {
                      mask = 0;
                    }else {
                      mask = 1;
                    }

                    var add = ' ';
                    if (j > 0) {
                      add = ' ';
                    }

                    final += add+_xmi+','+_ymi+','+_xma+','+_yma+','+mask;
              });
      }


  //Se imprime en la consola los puntos de los BBox
      console.log(final);
}
