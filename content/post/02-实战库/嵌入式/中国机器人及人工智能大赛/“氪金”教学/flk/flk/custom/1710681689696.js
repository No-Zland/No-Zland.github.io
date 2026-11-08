Blockly.Blocks['1710681689696'] = {
  init: function() {
    this.jsonInit({
      "type": "1710681689696",
      "message0": "抱块右转45度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710681689696'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(33)\nMOTOmove19(42,38,173,97,121,40,168,99,155,178,35,98,160,167,105,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(35)\nMOTOmove19(42,38,173,102,76,27,141,99,155,178,35,101,122,173,59,101,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710681689696'] = function(block) {
  let code = "robot.leju_action('抱块右转45度')\n";
  return code;
}

