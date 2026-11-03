Blockly.Blocks['1710421367219'] = {
  init: function() {
    this.jsonInit({
      "type": "1710421367219",
      "message0": "小转5度",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710421367219'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,93,112,58,151,99,120,170,100,93,142,136,106,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710421367219'] = function(block) {
  let code = "robot.leju_action('小转5度')\n";
  return code;
}

