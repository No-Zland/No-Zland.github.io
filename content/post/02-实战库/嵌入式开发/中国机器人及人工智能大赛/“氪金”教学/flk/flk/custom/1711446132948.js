Blockly.Blocks['1711446132948'] = {
  init: function() {
    this.jsonInit({
      "type": "1711446132948",
      "message0": "youyong",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711446132948'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(108,102,36,100,156,10,70,98,120,75,171,100,42,190,120,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(108,102,36,100,93,55,124,100,120,75,171,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711446132948'] = function(block) {
  let code = "robot.leju_action('youyong')\n";
  return code;
}

