# Program na rekrutecje dla firmy Hawatel
Wersje w innych językach:
<a href = https://github.com/MrResor/Hawatel_rekrutacja/blob/main/README.md>English </a>

## Sposób użycia
Program może być uruchomiony z konsoli przy użyciu 'python main.py', z 4 różnymi argumentami:</br>

### -h "help"
Wypisuje prosty teskt pomocniczy o skrypcie.

### -s "setup"
Upewnie się że baza danych ma tabele "product" która tak samo jak "currency" jest niezbędna do prawidłowego działania skryptu. Następnie, jeżeli tabela ta instnieje sprawdzamy czy tabela "currency" jest już stworzona. Jeżeli nie to tworzymy ją, uzupełniając ją przy okazji danymi otrzymanymi z API NBP odnośnie krusu wymiany walut EUR i USD. Jeżeli istnieje to sprawdzamy czy ma ona takie pola jakie są nam potrzebne. Jeżeli tak, dajmy znać że istnieje i odnotowujemy to w logu, jeżeli nie wypisujemy error do loga i zatrzymujemy skrypt.

### -u "update"
Aktualizuje tabele "currency" kursami walut otrzymanymi z API NBP. Jeżeli API nie posiada dzisiejszej wartości, drugie zapytanie jest wysyłane aby uzyskać ostatnią znaną wartość. Taki przypadek jest odnotowywany w logu. Następnie skrypt próbuje zaktualizować dane w tabeli, jednak w przypakdu błędu przerywa akcję. Jeżeli się uda lub nie, wynik operacji jest zapisywany w logu.

### -e "export"
Eksportuje dane do pliku .csv, aby były łatwe do przejrzenia w excelu. W wypadku jakiegokolwiek błedu process zostaje przerwany, a efekt zapisany w logu.

## Notatka
Zaktualizowany schemat bazy danych można znaleźć <a href = "https://github.com/MrResor/Hawatel_rekrutacja/blob/main/dbschema.txt">tutaj</a>. Jest to ten sam schemat który został dostarczony jako model bazy dancyh klienta z tabelą stworzoną przy użyciu opcji "-s" skryptu. Warto jednak dodać że dostarzona nam baza dancyh nie przechowuje poprawnie cen, gdyż ignoruje wszystkie wartości po przecinku(decimal(10,0) powinno zostać zamieniona na decimal(10,2)). Dodatkowo, przy użyciu danych dostarczonych do zapełnienia tabeli, nie dało się wstawić rekordów to tabeli "sellers". Było to spowodowane regułą która wymagała litery 'B' na 3ciej kolumnie, a wszystkie dane miałt tam litere 'S'.