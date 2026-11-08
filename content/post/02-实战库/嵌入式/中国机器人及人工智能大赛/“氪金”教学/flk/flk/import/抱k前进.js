Blockly.Blocks['1710886315365'] = {
  init: function() {
    this.jsonInit({
      "type": "1710886315365",
      "message0": "抱k前进",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710886315365'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(25,25,10,55,65,90,80,50,25,25,10,55,65,90,80,50,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(70, 10, 183, 99, 93, 54, 122, 90, 136, 190, 22, 98, 107, 146, 75, 95, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(70, 10, 183, 99, 115, 99, 103, 100, 136, 190, 22, 98, 109, 134, 89, 98, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 110, 74, 121, 100, 136, 190, 22, 98, 114, 137, 89, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 110, 61, 126, 104, 136, 190, 22, 98, 100, 127, 94, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(75)\nMOTOmove19(70, 10, 183, 99, 91, 66, 111, 102, 136, 190, 22, 98, 85, 101, 97, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 86, 63, 111, 100, 136, 190, 22, 98, 90, 126, 79, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(80)\nMOTOmove19(70, 10, 183, 99, 100, 73, 106, 100, 136, 190, 22, 98, 90, 139, 74, 96, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(65)\nMOTOmove19(70, 10, 183, 96, 95, 70, 110, 100, 136, 190, 22, 98, 109, 146, 75, 96, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(70, 10, 183, 100, 93, 55, 124, 100, 136, 190, 22, 98, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710886315365'] = function(block) {
  let code = "robot.leju_action('抱k前进')\n";
  return code;
}

