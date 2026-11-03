Blockly.Blocks['1711096167186'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096167186",
      "message0": "q-box-Lmove",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096167186'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,14,20,65,85,95,85,35,20,20,20,65,55,55,55,35,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 72, 100, 68, 111, 84, 139, 190, 23, 119, 106, 154, 68, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(50)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096167186'] = function(block) {
  let code = "robot.leju_action('q-box-Lmove')\n";
  return code;
}

