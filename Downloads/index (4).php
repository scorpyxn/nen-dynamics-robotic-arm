<html>
	<head>
		<meta charset="UTF-8">
		<title>Robotersteuerung</title>
		<?php
	
			$host = "localhost";
			$benutzer = "root";
			$kenn = "123";
			$db = mysqli_connect($host, $benutzer, $kenn, "motoren")or exit("keine verbindung m&ouml;glich");
			$sqlbef = "SELECT * FROM Startpos;";
			$sqlbef = "where motor1;
			$sqlerg = mysqli_query ($db, $sqlbef);
			$anz = mysqli_num_rows($sqlerg);
						$motor1 = "SELECT (motor1) from pos;";
			$motor2 = "SELECT (motor1) from pos;";
			$motor3 = "SELECT (motor1) from pos;";
			$motor4 = "SELECT (motor1) from pos;";
			$motor5 = "SELECT (motor1) from pos;";
			$motor6 = "SELECT (motor1) from pos;";
			echo $motor1;
			echo $motor2;
			echo $motor3;
			echo $motor4;
			echo $motor5;
			echo $motor6;
			mysqli_close ($db);
		?>
		<script type="text/javascript">	
				var dreht = 1.5;
				var untera = 0.7;
				var obera = 1.5;
				var handg0 = 2.5;
				var handg1 = 1.5;
				var krallev = 1.5;
				function dreh(i) { 
			   	  dreht = dreht + i;
				  if (dreht > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					dreht = 2.5;
				  }
				  else if (dreht < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					dreht = 0.5;
				  }
				  document.getElementById ("drehteller").value = dreht;
				}; 	
				function unterarm(i) { 
			   	  untera = untera + i;
				  if (untera > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					untera = 2.5;
				  }
				  else if (untera < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					untera = 0.5;
				  }
				  document.getElementById ("arm0").value = untera;
				};
				function oberarm(i) { 
			   	  obera = obera + i;
				  if (obera > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					obera = 2.5;
				  }
				  else if (obera < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					obera = 0.5;
				  }
				  document.getElementById ("arm1").value = obera;
				}; 	
				function handgelenk0(i) { 
			   	  handg0 = handg0 + i; 
				  if (handg0 > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					handg0 = 2.5;
				  }
				  else if (handg0 < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					handg0 = 0.5;
				  }
				  document.getElementById ("hand0").value = handg0;
				}; 	
				function handgelenk1(i) { 
			   	  handg1 = handg1 + i;
				  if (handg1 > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					handg1 = 2.5;
				  }
				  else if (handg1 < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					handg1 = 0.5;
				  }
				  document.getElementById ("hand1").value = handg1;
				}; 	
				function krallen_griff(i) { 
			   	  krallev = krallev + i;
				   if (krallev > 2.5)
				  {
				    alert("2.5 ist das Maximum");
					krallev = 2.5;
				  }
				  else if (krallev < 0.5)
				  {
				    alert("0.5 ist das Minimum");
					krallev = 0.5;
				  }
				  document.getElementById ("kralle").value = krallev;
				};	
   		</script>
   		<noscript>
    		Sie haben JavaScript deaktiviert.
   		</noscript>
	</head>
	<body>
		<a href="test.php">klick mich bitte<a>
		<form action="index.php" method="post">
			Drehteller Position:<br>
			
 			<input type="text" id="drehteller" name="motor1">
			<input type="submit" onclick="dreh(1)"value="+1">
 			<input type="submit" onclick="dreh(0.1)"value="+0.1">
			<input type="submit" onclick="dreh(-0.1)" value="-0.1">
			<input type="submit" onclick="dreh(-1)" value="-1">
		</form>
		<form action="index.php" method="post">
			Unterarm Position:<br>
			<button type="button" onclick="unterarm(-0.1)">-0.1</button>
			<button type="button" onclick="unterarm(-1)">-1</button>
 			<input type="text" id="arm0" name="motor2">
			<button type="button" onclick="unterarm(1)">+1</button>
 			<button type="button" onclick="unterarm(0.1)">+0.1</button>
		</form>
		<form action="index.php" method="post">
			Oberarm Position:<br>
			<button type="button" onclick="oberarm(-0.1)">-0.1</button>
			<button type="button" onclick="oberarm(-1)">-1</button>
 		 	<input type="text" id="arm1" name="motor3">
			<button type="button" onclick="oberarm(1)">+1</button>
 			<button type="button" onclick="oberarm(0.1)">+0.1</button>
		</form>
		<form action="index.php" method="post">
			Unteres Handgelenk Position:<br>
			<button type="button" onclick="handgelenk0(-0.1)">-0.1</button>
			<button type="button" onclick="handgelenk0(-1)">-1</button>
 		 	<input type="text" id="hand0" name="motor4">
			<button type="button" onclick="handgelenk0(1)">+1</button>
 			<button type="button" onclick="handgelenk0(0.1)">+0.1</button>
		</form>
		<form action="index.php" method="post">
			Handgelenk Position:<br>
			<button type="button" onclick="handgelenk1(-0.1)">-0.1</button>
			<button type="button" onclick="handgelenk1(-1)">-1</button>
 		 	<input type="text" id="hand1" name="motor5">
			<button type="button" onclick="handgelenk1(1)">+1</button>
 			<button type="button" onclick="handgelenk1(0.1)">+0.1</button>
		</form>
		<form action="index.php" method="post">
			Position der Kralle:<br>
			<button type="button" onclick="krallen_griff(-0.1)">-0.1</button>
			<button type="button" onclick="krallen_griff(-1)">-1</button>
 		 	<input type="text" id="kralle" name="motor6">
			<button type="button" onclick="krallen_griff(1)">+1</button>
 			<button type="button" onclick="krallen_griff(0.1)">+0.1</button>
		</form>
		<script type="text/javascript">
			document.getElementById ("drehteller").value = dreht;
			document.getElementById ("arm0").value = untera;	
			document.getElementById ("arm1").value = obera;
			document.getElementById ("hand0").value = handg0;
			document.getElementById ("hand1").value = handg1;
			document.getElementById ("kralle").value = krallev;	
   		</script>
		<br>das ergebnis ist bitte:<br>
		<?php
			echo $_POST["motor1"];
		?>
		<?php
		$connection = mysql_connect("localhost","root_user","root_password")
         or die("problems connecting to DB.");

		mysql_select_db("my_database",$connection) 
         or  die("Problems selecting DB.");

		$records = mysql_query("select id, name, school from students",$connection) 
         or die("Problems on querying " . mysql_error() );

		while ($record = mysql_fetch_array($records)) {
			echo "id: " . $record['id'] . "<br>";
			echo "name: " . $record['nombre'] . "<br>";
			echo "school: " . $record['school'] . "<br>";
		}
		mysq_close($connection);
		?>
	</body>
</html>