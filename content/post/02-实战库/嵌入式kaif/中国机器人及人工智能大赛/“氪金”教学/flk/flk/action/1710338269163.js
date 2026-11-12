Blockly.Blocks['1710338269163'] = {
  init: function() {
    this.jsonInit({
      "type": "1710338269163",
      "message0": "抱块右转30度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710338269163'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,97,121,40,167,100,155,178,35,96,156,167,104,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,102,76,27,141,99,155,178,35,101,122,173,59,101,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710338269163'] = function(block) {
  let code = "robot.leju_action('抱块右转30度')\n";
  return code;
}

