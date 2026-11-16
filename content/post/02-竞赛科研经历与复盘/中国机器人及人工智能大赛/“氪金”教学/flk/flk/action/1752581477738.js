Blockly.Blocks['1752581477738'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581477738",
      "message0": "叠块退",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581477738'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(15)\nMOTOmove19(58,24,190,105,93,55,124,108,123,188,10,111,102,136,78,112,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,105,93,55,124,107,123,188,10,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(58,24,190,92,116,55,144,85,123,188,10,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,89,114,89,104,98,123,188,10,93,104,145,77,91,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(58,24,190,100,93,55,124,98,123,188,10,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1752581477738'] = function(block) {
  let code = "robot.leju_action('叠块退')\n";
  return code;
}

