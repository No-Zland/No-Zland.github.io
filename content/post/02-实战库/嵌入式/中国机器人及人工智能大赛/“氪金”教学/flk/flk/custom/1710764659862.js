Blockly.Blocks['1710764659862'] = {
  init: function() {
    this.jsonInit({
      "type": "1710764659862",
      "message0": "左转5度pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710764659862'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,98,85,82,82,99,120,170,100,97,71,148,44,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710764659862'] = function(block) {
  let code = "robot.leju_action('左转5度pro')\n";
  return code;
}

