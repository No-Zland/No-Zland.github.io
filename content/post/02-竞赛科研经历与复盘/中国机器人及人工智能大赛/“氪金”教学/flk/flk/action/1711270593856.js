Blockly.Blocks['1711270593856'] = {
  init: function() {
    this.jsonInit({
      "type": "1711270593856",
      "message0": "sgt1bx",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711270593856'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(5)\nMOTOmove19(80,30,100,100,93,58,124,114,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,58,124,114,120,170,100,102,94,71,134,113,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,58,124,114,120,170,100,101,73,97,87,112,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,103,69,92,59,110,120,170,100,107,48,153,10,114,128,71,100)\nMOTOwait()\nMOTOsetspeed(18)\nMOTOmove19(80,30,100,108,77,76,75,100,120,170,100,108,44,159,10,101,128,71,100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(80,30,100,105,80,32,113,94,119,170,20,104,40,182,10,93,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,105,73,34,83,94,119,157,10,104,40,182,10,93,128,71,100)\nMOTOwait()\nMOTOsetspeed(25)\nMOTOmove19(80,30,100,94,95,34,106,76,119,169,10,105,40,190,16,85,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,104,160,97,99,94,119,169,18,105,40,190,16,85,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,104,151,19,168,87,120,170,100,104,40,190,15,86,128,71,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(80,30,100,99,160,10,190,99,120,170,100,104,40,190,10,105,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711270593856'] = function(block) {
  let code = "robot.leju_action('sgt1bx')\n";
  return code;
}

