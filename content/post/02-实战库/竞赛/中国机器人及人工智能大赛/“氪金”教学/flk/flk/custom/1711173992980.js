Blockly.Blocks['1711173992980'] = {
  init: function() {
    this.jsonInit({
      "type": "1711173992980",
      "message0": "dbbox_back_x",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711173992980'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(50)\nMOTOmove19(66,21,190,105,93,55,124,108,129,174,10,111,102,136,78,112,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,105,93,55,124,107,129,174,10,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(66,21,190,92,116,55,144,85,129,174,10,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,92,75,55,106,95,129,174,10,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,105,93,55,124,107,129,174,10,108,84,141,56,115,120,40,100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(66,21,190,105,92,55,124,107,129,174,10,111,107,136,78,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,21,190,100,93,55,124,98,129,174,10,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1711173992980'] = function(block) {
  let code = "robot.leju_action('dbbox_back_x')\n";
  return code;
}

