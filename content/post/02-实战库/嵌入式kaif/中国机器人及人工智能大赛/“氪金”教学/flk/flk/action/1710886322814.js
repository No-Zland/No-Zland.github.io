Blockly.Blocks['1710886322814'] = {
  init: function() {
    this.jsonInit({
      "type": "1710886322814",
      "message0": "抱k后退",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710886322814'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 100, 93, 55, 124, 100, 138, 186, 24, 100, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(60, 13, 177, 85, 91, 50, 128, 88, 138, 186, 24, 95, 117, 168, 62, 90, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(60, 13, 177, 88, 91, 48, 129, 88, 138, 186, 24, 94, 107, 146, 76, 87, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 86, 90, 95, 84, 90, 138, 186, 24, 94, 107, 146, 78, 87, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 88, 84, 53, 115, 85, 138, 186, 24, 93, 104, 144, 78, 91, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(60, 13, 177, 106, 93, 53, 124, 113, 138, 186, 24, 114, 102, 154, 55, 110, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60, 13, 177, 106, 93, 53, 124, 113, 138, 186, 24, 114, 95, 105, 95, 110, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(60, 13, 177, 104, 83, 32, 135, 111, 138, 186, 24, 115, 111, 150, 72, 112, 120, 80, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(60, 13, 177, 100, 93, 55, 124, 100, 138, 186, 24, 100, 107, 145, 76, 100, 120, 80, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710886322814'] = function(block) {
  let code = "robot.leju_action('抱k后退')\n";
  return code;
}

