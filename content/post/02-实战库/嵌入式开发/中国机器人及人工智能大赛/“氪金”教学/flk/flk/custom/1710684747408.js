Blockly.Blocks['1710684747408'] = {
  init: function() {
    this.jsonInit({
      "type": "1710684747408",
      "message0": "包块右转Pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710684747408'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,97,121,40,167,100,155,178,35,96,156,167,104,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,100,93,55,124,100,155,178,35,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710684747408'] = function(block) {
  let code = "robot.leju_action('包块右转Pro')\n";
  return code;
}

