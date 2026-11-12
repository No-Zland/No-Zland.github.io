Blockly.Blocks['1710684923140'] = {
  init: function() {
    this.jsonInit({
      "type": "1710684923140",
      "message0": "抱块左转Pro",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710684923140'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(41,37,172,95,49,50,87,96,154,178,35,97,88,181,20,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(41,37,172,100,93,55,124,100,154,178,35,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710684923140'] = function(block) {
  let code = "robot.leju_action('抱块左转Pro')\n";
  return code;
}

