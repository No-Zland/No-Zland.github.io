Blockly.Blocks['1711173425441'] = {
  init: function() {
    this.jsonInit({
      "type": "1711173425441",
      "message0": "x_doublebox_Lmove",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711173425441'] = function(block) {
  let code = "MOTOrigid16(20,14,20,65,85,95,85,35,20,20,20,65,55,55,55,35)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,72,100,68,111,84,129,174,10,119,106,154,68,100,120,40,100)\nMOTOwait()\nDelayMs(50)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,93,55,124,100,129,174,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711173425441'] = function(block) {
  let code = "robot.leju_action('x_doublebox_Lmove')\n";
  return code;
}

