# Program na rekrutecje dla firmy Hawatel
Wersje w innych językach:
<a href = https://github.com/MrResor/Hawatel_rekrutacja/blob/main/README.md>English </a>

## Sposób użycia
Program może być uruchomiony z konsoli przy użyciu 'python main.py', z 4 różnymi argumentami:</br>
-h  wyświetla tekst pomocniczy,</br>
-s  przygotowuje baze danych przez dodanie tabeli "currency" która jest niezbędna do poprawnego działania skryptu,</br>
-u  aktualizuje kursy walut w tabeli "currency",</br>
-e  eksportuje dane do pliku .csv</br>

### -h "help"
Wypisuje prosty teskt pomocniczy o skrypcie.

### -s "setup"
Upewnie się że baza danych ma tabele "product" która tak samo jak "currency" jest niezbędna do prawidłowego działania skryptu. Następnie, jeżeli tabela ta instnieje sprawdzamy czy tabela "currency" jest już stworzona. Jeżeli nie to tworzymy ją, uzupełniając ją przy okazji danymi otrzymanymi z API NBP odnośnie krusu wymiany walut EUR i USD. Jeżeli istnieje to sprawdzamy czy ma ona takie pola jakie są nam potrzebne. Jeżeli tak, dajmy znać że istnieje i odnotowujemy to w logu, jeżeli nie wypisujemy error do loga i zatrzymujemy skrypt.

### -u "update"
Aktualizuje tabele "currency" kursami walut otrzymanymi z API NBP. Jeżeli API nie posiada dzisiejszej wartości, drugie zapytanie jest wysyłane aby uzyskać ostatnią znaną wartość. Taki przypadek jest odnotowywany w logu. Następnie skrypt próbuje zaktualizować dane w tabeli, jednak w przypakdu błędu przerywa akcję. Jeżeli się uda lub nie, wynik operacji jest zapisywany w logu.

### -e "export"
Eksportuje dane do pliku .csv, aby były łatwe do przejrzenia w excelu. W wypadku jakiegokolwiek błedu process zostaje przerwany, a efekt zapisany w logu.