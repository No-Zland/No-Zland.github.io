Blockly.Blocks['1711430372158'] = {
  init: function() {
    this.jsonInit({
      "type": "1711430372158",
      "message0": "sgt-头改",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711430372158'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,93,55,124,100,120,170,41,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,99,93,54,101,99,120,170,41,100,108,144,100,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(50,88,161,99,93,54,101,99,145,121,40,100,108,144,100,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(50,88,161,100,86,61,64,99,145,121,40,100,118,143,135,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(86,87,165,100,86,61,64,99,134,94,40,100,118,143,135,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,93,55,124,100,120,170,41,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(76,28,161,100,156,10,109,98,120,170,41,100,42,190,93,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711430372158'] = function(block) {
  let code = "robot.leju_action('sgt-头改')\n";
  return code;
}

