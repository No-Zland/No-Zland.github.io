Blockly.Blocks['1711096159612'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096159612",
      "message0": "q-box-Rmove",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096159612'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,65,55,55,55,35,20,20,20,65,85,95,85,35,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 90, 93, 50, 130, 95, 139, 190, 23, 134, 97, 124, 88, 116, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(67, 14, 180, 100, 93, 55, 124, 100, 139, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096159612'] = function(block) {
  let code = "robot.leju_action('q-box-Rmove')\n";
  return code;
}

