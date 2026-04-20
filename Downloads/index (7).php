<html>
	<head>
		<meta charset="UTF-8">
		<title>Robotersteuerung</title>
				<script type="text/javascript">	
				var dreht = 1.5;
				var untera = 0.8;
				var obera = 1.35;
				var handg0 = 1.9;
				var handg1 = 0.9;
				var krallev = 1.15;
				function dreh(i) {
				  dreht = dreht + i;
				  if (dreht > 2.5) {
					dreht = 2.5;
				  } else if (dreht < 0.5) {
					dreht = 0.5;
				  } 
				  document.getElementById ("drehteller").value = dreht; //schreibe das Ergebnis in das Formularfeld des Drehtellers.
				}	
				function unterarm(i) { 
				  untera = untera + i;
				  if (untera > 1.3) {
					untera = 1.3;
				  } else if (untera < 0.5) {
					untera = 0.5;
				  }
				  document.getElementById ("arm0").value = untera; //schreibe das Ergebnis in das Formularfeld des Unterarms.
				}
				function oberarm(i) { 
			   	  obera = obera + i;
				  if (obera > 1.8) {
					obera = 1.8;
				  } else if (obera < 1.3) {
					obera = 1.3;
				  }
				  document.getElementById ("arm1").value = obera; //schreibe das Ergebnis in das Formularfeld des Oberarms.
				}	
				function handgelenk0(i) { 
			   	  handg0 = handg0 + i; 
				  if (handg0 > 2.5) {
					handg0 = 2.5;
				  } else if (handg0 < 1.2) {
					handg0 = 1.2;
				  }
				  document.getElementById ("hand0").value = handg0; //schreibe das Ergebnis in das Formularfeld des unteren Handgelenks. 
				} 	
				function handgelenk1(i) { 
			   	  handg1 = handg1 + i;
				  if (handg1 > 1.9) {
					handg1 = 1.9;
				  } else if (handg1 < 0.9) {
					handg1 = 0.9;
				  }
				  document.getElementById ("hand1").value = handg1; //schreibe das Ergebnis in das Formularfeld des oberen Handgelenks. 
				}	
				function krallen_griff(i) { 
			   	  krallev = krallev + i;
				   if (krallev > 2){
					krallev = 2;
				  } else if (krallev < 1.05) {
					krallev = 1.05;
				  }
				  document.getElementById ("kralle").value = krallev; //schreibe das Ergebnis in das Formularfeld der Kralle.
				}
				function LimitCheck() {
					if (dreht == 2.5) {
						//document.getElementById("D").style.color = "Blue";
						document.getElementById("D").textContent = " ← am oberen Limit";
					} else if (dreht == 0.5) {
						//document.getElementById("D").style.color = "Blue";
						document.getElementById("D").textContent = " ← am unteren Limit";
					}
					if (untera == 1.3) {
						//document.getElementById("U").style.color = "Blue";
						document.getElementById("U").textContent = " ← am oberen Limit";
					} else if (untera == 0.5) {
						//document.getElementById("U").style.color = "Blue";
						document.getElementById("U").textContent = " ← am unteren Limit";
					}
					if (obera == 1.8) {
						//document.getElementById("O").style.color = "Blue";
						document.getElementById("O").textContent = " ← am oberen Limit";
					} else if (obera == 1.3) {
						//document.getElementById("O").style.color = "Blue";
						document.getElementById("O").textContent = " ← am unteren Limit";
					}
					if (handg0 == 2.5) {
						//document.getElementById("H0").style.color = "Blue";
						document.getElementById("H0").textContent = " ← am oberen Limit";
					} else if (handg0 == 1.2) {
						//document.getElementById("H0").style.color = "Blue";
						document.getElementById("H0").textContent = " ← am unteren Limit";
					}
					if (handg1 == 1.9) {
						//document.getElementById("H1").style.color = "Blue";
						document.getElementById("H1").textContent = " ← am oberen Limit";
					} else if (handg1 == 0.9) {
						//document.getElementById("H1").style.color = "Blue";
						document.getElementById("H1").textContent = " ← am unteren Limit";
					} 
					if (krallev == 2) {
						//document.getElementById("K").style.color = "Blue";
						document.getElementById("K").textContent = " ← am oberen Limit";
					} else if (krallev == 1.05) {
						//document.getElementById("K").style.color = "Blue";
						document.getElementById("K").textContent = " ← am unteren Limit";
					}
				}
				function Eintragen() {
					document.getElementById("drehteller").value = dreht; 
					document.getElementById("arm0").value = untera;	
					document.getElementById("arm1").value = obera;
					document.getElementById("hand0").value = handg0;
					document.getElementById("hand1").value = handg1;
					document.getElementById("kralle").value = krallev;
				}
				function close() {
					window.close();
				}

   		</script>
   		<noscript>
    		Sie haben JavaScript deaktiviert :'(
   		</noscript>
	</head>

	<style type="text/css">
	body {background-image:url(arm.jpg);background-repeat:no-repeat; }
	</style>


	<body onload="LimitCheck(), Eintragen()">
		<div align="right" >
		<table border="0">
			<tr>
				<td>
				<br><form action="index.php" method="post">
					Position der Kralle:<a id="K" style="color: blue;"></a><br>
					auf&nbsp;&nbsp; <input type="submit" onclick="krallen_griff(0.1)" value="+0.10">
					<input type="submit" onclick="krallen_griff(0.05)" value="+0.05">
					<input type="text" id="kralle" name="motor6"> <!--anzeige der Position der Kralle-->
					<input type="submit" onclick="krallen_griff(-0.05)" value="-0.05">
					<input type="submit" onclick="krallen_griff(-0.1)" value="-0.10"> zu			
					<br><br>
					Position des Handdreheglenks:<a id="H1" style="color: blue;"></a><br>
					hoch <input type="submit" onclick="handgelenk1(0.5)" value="+0.50">
					<input type="submit" onclick="handgelenk1(0.05)" value="+0.05">
					<input type="text" id="hand1" name="motor5"> <!--anzeige der Position des oberen Handgelenks-->
					<input type="submit" onclick="handgelenk1(-0.05)" value="-0.05">
					<input type="submit" onclick="handgelenk1(-0.5)" value="-0.50"> runter
					<br><br>
					Position des Unteren Handgelenks:<a id="H0" style="color: blue;"></a><br>
					hoch <input type="submit" onclick="handgelenk0(0.5)" value="+0.50">
					<input type="submit" onclick="handgelenk0(0.05)" value="+0.05">
					<input type="text" id="hand0" name="motor4"> <!--anzeige der Position des unteren Handgelenks-->
					<input type="submit" onclick="handgelenk0(-0.05)" value="-0.05">
					<input type="submit" onclick="handgelenk0(-0.5)" value="-0.50"> runter
					<br><br>
					Position des Oberarms:<a id="O" style="color: blue;"></a><br>
					hoch <input type="submit" onclick="oberarm(0.5)" value="+0.50">
					<input type="submit" onclick="oberarm(0.05)" value="+0.05">
					<input type="text" id="arm1" name="motor3"> <!--anzeige der Position des Oberarms-->
					<input type="submit" onclick="oberarm(-0.05)" value="-0.05">
					<input type="submit" onclick="oberarm(-0.5)" value="-0.50"> runter
					<br><br>
					Position des Unterarms:<a id="U" style="color: blue;"></a><br>
					hoch <input type="submit" onclick="unterarm(0.5)" value="+0.50">
					<input type="submit" onclick="unterarm(0.05)" value="+0.05">
					<input type="text" id="arm0" name="motor2"> <!--anzeige der Position des Unterarms-->
					<input type="submit" onclick="unterarm(-0.05)" value="-0.05">
					<input type="submit" onclick="unterarm(-0.5)" value="-0.50"> runter 
					<br><br>
					Position des Drehtellers:<a id="D" style="color: blue;"></a><br>
					links <input type="submit" onclick="dreh(1.0)" value="+1.00">
					<input type="submit" onclick="dreh(0.1)" value="+0.10">
					<input type="text" id="drehteller" name="motor1"> <!--anzeige der Position des Drehtellers-->
					<input type="submit" onclick="dreh(-0.1)" value="-0.10">
					<input type="submit" onclick="dreh(-1.0)" value="-1.00"> rechts
				</form>
				<div align="center">
				<form action="index.php" method="post">
					<input type="hidden" name="motor1" value="1.5">
					<input type="hidden" name="motor2" value="0.8">
					<input type="hidden" name="motor3" value="1.35">
					<input type="hidden" name="motor4" value="1.9">
					<input type="hidden" name="motor5" value="0.9">
					<input type="hidden" name="motor6" value="1.15">
					<input type="submit" value="Alle Motoren auf Startposition"> <!--Knopf zum resetten der Motoren-->
				</form>
				</div>
				</td>
			</tr>
		</table>
		</div>
		<input type="button" onclick="close()" value="[]">
		