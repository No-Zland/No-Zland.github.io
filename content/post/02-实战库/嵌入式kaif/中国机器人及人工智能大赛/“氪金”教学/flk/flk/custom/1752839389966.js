Blockly.Blocks['1752839389966'] = {
  init: function() {
    this.jsonInit({
      "type": "1752839389966",
      "message0": "1bazk",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752839389966'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(15)\nMOTOmove19(64,10,164,105,93,55,124,108,138,190,37,111,102,136,78,112,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,93,55,124,107,138,190,37,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64,10,164,92,116,55,144,85,138,190,37,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,89,114,89,104,98,138,190,37,93,104,145,77,91,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64,10,164,100,93,55,124,98,138,190,37,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1752839389966'] = function(block) {
  let code = "robot.leju_action('1bazk')\n";
  return code;
}

