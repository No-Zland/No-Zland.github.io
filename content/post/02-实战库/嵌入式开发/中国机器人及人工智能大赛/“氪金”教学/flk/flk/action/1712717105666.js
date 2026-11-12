Blockly.Blocks['1712717105666'] = {
  init: function() {
    this.jsonInit({
      "type": "1712717105666",
      "message0": "高台box-back",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1712717105666'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,100,93,55,124,100,122,190,31,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(75,10,169,105,93,55,124,108,122,190,31,111,102,136,78,112,120,40,100)\nMOTOwait()\nDelayMs(100)\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,105,93,55,124,107,122,190,31,107,136,154,91,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(75,10,169,92,116,55,144,85,122,190,31,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,92,75,55,106,95,122,190,31,95,107,145,76,93,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,105,93,55,124,107,122,190,31,108,84,141,56,115,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,105,92,55,124,107,122,190,31,111,107,136,78,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(75,10,169,100,93,55,124,98,122,190,31,100,107,145,76,102,120,40,100)\nMOTOwait()\nDelayMs(100)\n";
  return code;
}

Blockly.Python['1712717105666'] = function(block) {
  let code = "robot.leju_action('高台box-back')\n";
  return code;
}

