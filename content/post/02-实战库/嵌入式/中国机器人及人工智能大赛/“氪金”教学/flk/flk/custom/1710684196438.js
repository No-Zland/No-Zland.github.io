Blockly.Blocks['1710684196438'] = {
  init: function() {
    this.jsonInit({
      "type": "1710684196438",
      "message0": "左转5度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710684196438'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,98,102,83,100,99,120,170,100,98,77,139,58,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710684196438'] = function(block) {
  let code = "robot.leju_action('左转5度')\n";
  return code;
}

