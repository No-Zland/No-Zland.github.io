Blockly.Blocks['1719142277430'] = {
  init: function() {
    this.jsonInit({
      "type": "1719142277430",
      "message0": "box-back-q2",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719142277430'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,93,55,124,108,137,190,37,111,101,136,78,130,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,105,93,55,124,107,137,190,37,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,90,115,55,143,73,137,190,37,95,107,145,76,93,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,87,111,87,98,85,137,190,37,89,104,143,77,86,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64,10,164,100,93,55,124,98,137,190,37,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1719142277430'] = function(block) {
  let code = "robot.leju_action('box-back-q2')\n";
  return code;
}

