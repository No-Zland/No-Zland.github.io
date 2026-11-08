Blockly.Blocks['1711096125443'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096125443",
      "message0": "Rturn-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096125443'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 99, 160, 49, 190, 100, 120, 170, 85, 100, 161, 135, 148, 98, 120, 40, 100)\nMOTOwait()\nDelayMs(150)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096125443'] = function(block) {
  let code = "robot.leju_action('Rturn-q')\n";
  return code;
}

