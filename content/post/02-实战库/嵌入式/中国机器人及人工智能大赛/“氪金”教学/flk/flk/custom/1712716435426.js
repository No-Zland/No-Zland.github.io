Blockly.Blocks['1712716435426'] = {
  init: function() {
    this.jsonInit({
      "type": "1712716435426",
      "message0": "高台box-up",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1712716435426'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,43,93,88,148,150,69,92,120,168,115,95,43,50,116,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(74,80,157,88,148,150,69,92,114,133,44,95,43,50,116,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,80,157,65,130,145,46,67,114,133,44,131,64,50,155,126,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,69,124,139,47,72,122,190,31,128,67,52,152,126,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,10,169,91,114,150,48,90,122,190,31,114,84,50,151,112,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(75,10,169,100,93,55,124,100,122,190,31,99,107,144,75,99,120,40,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1712716435426'] = function(block) {
  let code = "robot.leju_action('高台box-up')\n";
  return code;
}

