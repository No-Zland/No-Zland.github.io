Blockly.Blocks['1711096138807'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096138807",
      "message0": "q-box-back",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096138807'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 108, 137, 190, 23, 111, 102, 136, 78, 112, 120, 40, 100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 107, 137, 190, 23, 107, 136, 154, 91, 103, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(71, 10, 180, 92, 116, 55, 144, 85, 137, 190, 23, 95, 107, 145, 76, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 92, 75, 55, 106, 95, 137, 190, 23, 95, 107, 145, 76, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 105, 93, 55, 124, 107, 137, 190, 23, 108, 84, 141, 56, 115, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(71, 10, 180, 105, 92, 55, 124, 107, 137, 190, 23, 111, 107, 136, 78, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(71, 10, 180, 100, 93, 55, 124, 98, 137, 190, 23, 100, 107, 145, 76, 102, 120, 40, 100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1711096138807'] = function(block) {
  let code = "robot.leju_action('q-box-back')\n";
  return code;
}

