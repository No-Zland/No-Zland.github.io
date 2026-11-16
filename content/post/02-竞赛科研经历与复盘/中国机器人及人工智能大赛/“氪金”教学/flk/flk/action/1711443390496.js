Blockly.Blocks['1711443390496'] = {
  init: function() {
    this.jsonInit({
      "type": "1711443390496",
      "message0": "box_back_dg",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711443390496'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(64,10,164,105,93,55,124,108,137,190,37,111,102,136,78,112,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,93,55,124,107,137,190,37,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64,10,164,92,116,55,144,85,137,190,37,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,92,75,55,106,95,137,190,37,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,93,55,124,107,137,190,37,108,84,141,56,115,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64,10,164,105,92,55,124,107,137,190,37,111,107,136,78,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,98,137,190,37,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1711443390496'] = function(block) {
  let code = "robot.leju_action('box_back_dg')\n";
  return code;
}

