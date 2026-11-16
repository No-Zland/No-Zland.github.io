Blockly.Blocks['1719138675327'] = {
  init: function() {
    this.jsonInit({
      "type": "1719138675327",
      "message0": "box2-up",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1719138675327'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,43,93,88,148,150,69,92,120,168,115,95,43,50,116,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(74,80,157,88,148,150,69,92,114,133,44,95,43,50,116,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,80,157,65,130,145,46,67,114,133,44,131,64,50,155,126,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(63,27,144,69,124,139,47,72,119,188,55,128,67,52,152,126,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(63,27,144,91,114,150,48,90,119,188,55,114,84,50,151,112,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(63,27,144,100,93,55,124,100,119,188,55,99,107,144,75,99,120,40,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1719138675327'] = function(block) {
  let code = "robot.leju_action('box2-up')\n";
  return code;
}

