Blockly.Blocks['1710339461304'] = {
  init: function() {
    this.jsonInit({
      "type": "1710339461304",
      "message0": "抱块左转30度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710339461304'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(40)\nMOTOmove19(41,37,172,109,44,49,85,100,154,178,35,106,83,183,10,101,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(42,38,173,99,89,23,145,100,155,178,35,98,111,182,51,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710339461304'] = function(block) {
  let code = "robot.leju_action('抱块左转30度')\n";
  return code;
}

