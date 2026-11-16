Blockly.Blocks['1711096148448'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096148448",
      "message0": "q-L-turn",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096148448'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 107, 89, 106, 59, 103, 120, 170, 100, 105, 51, 152, 21, 98, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096148448'] = function(block) {
  let code = "robot.leju_action('q-L-turn')\n";
  return code;
}

