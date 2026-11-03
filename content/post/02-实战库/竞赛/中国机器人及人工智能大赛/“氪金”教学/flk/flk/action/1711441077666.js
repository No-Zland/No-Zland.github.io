Blockly.Blocks['1711441077666'] = {
  init: function() {
    this.jsonInit({
      "type": "1711441077666",
      "message0": "box-down1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711441077666'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(50)\nMOTOmove19(60,15,190,100,93,55,130,98,132,187,10,100,107,145,70,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(60,15,190,62,109,150,46,74,132,187,10,128,103,59,154,131,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(72,14,147,71,122,150,47,69,130,176,57,135,79,50,152,133,120,40,100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(72,14,147,99,98,150,40,100,130,176,57,100,105,50,163,99,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711441077666'] = function(block) {
  let code = "robot.leju_action('box-down1')\n";
  return code;
}

