# Prosty program aktualizujący kursy walut w bazie danych MySQL
Wersje w innych językach:
<a href = https://github.com/MrResor/currency_includer/blob/main/README.md>English </a>

## Krótki opis
Skrypt będący w stanie połączyć się z istniejącą bazą donych, zmodyfikować ją przez dodanie tabeli "currency", wypełnić ją  obecnymi wartościami kursów walut i wyeksportować zebrane dane do pliku .csv. Obecne kursy walut pobierane są z API NBP, i jeżeli tabela "currency" została wcześniej poprawnie stworzona możliwe jest wyłącznie zaktualizowanie kursów walut przy użyciu odpowiedniej komendy. To samo tyczy się eksportowania danych z tabeli "product" z dodanymi cenami w USD i EUR.
## Sposób użycia
Program może być uruchomiony z konsoli przy użyciu 'python main.py', z 4 różnymi argumentami:</br>

### -h, --help
Wypisuje prosty teskt pomocniczy o skrypcie.

### -s --setup
Upewnie się że baza danych ma tabele "product" która jest niezbędna do prawidłowego działania skryptu. Następnie, jeżeli tabela ta istnieje próbuje stworzyć tabelę "currency". W przypadku gdy tabela ta już istnieje, sprawdzana jest jej poprawność, i jeśli jest ona zgodna z oczekiwaniami użytkownik jest o tym fakcie informowany. W przeciwnym wypadku pojawią się informacja o błędzie. Po udanym stworzeniu tabeli wysyłane jest zapytanie GET jest wysłane do API NBP aby otrzymać aktualne kursy walut dla USD i EUR którymi tabela zostanie wypełniona. Jeżeli istnieje to sprawdzamy czy ma ona takie pola jakie są nam potrzebne. W przypadku gdy tabela "product" nie istnieje, użytkownik jest informowany o błędzie.

### -u, --update
Aktualizuje tabele "currency" kursami walut otrzymanymi z API NBP. Jeżeli API nie posiada dzisiejszej wartości, drugie zapytanie jest wysyłane aby uzyskać ostatnią znaną wartość. Taki przypadek jest odnotowywany w logu. Następnie skrypt próbuje zaktualizować dane w tabeli, jednak w przypakdu błędu przerywa akcję. Wynik operacji jest zapisywany w logu, niezależnie od tego czy została ona wykonana poprawnie czy nie.

### -e, --export
Eksportuje dane do pliku .csv, aby były łatwe do przejrzenia w excelu. W wypadku jakiegokolwiek błedu process zostaje przerwany, a efekt zapisany w logu.

## Kody wyjściowe
&nbsp;&nbsp;&nbsp;0 - Program zakończył działanie poprawnie.  
&nbsp;&nbsp;&nbsp;2 - Błąd połącznia z bazą danych (niepoprawne dane logowania, baza danych nie istnieje, baza danych nie odpowiada).  
&nbsp;&nbsp;&nbsp;3 - Błąd połączenia z API.  
&nbsp;&nbsp;&nbsp;4 - Niepoprawne tabele w bazie dancyh (brak tabeli "product", brak tabeli "currency", tabela "currency" istnieje ale jest niepoprawna.)  
W przypadku wystąpienia jakiegokolwiek błędu, zalecane jest odniesienie się do pliku logu obecnego w folderze skryptu.

## Notatka
Zaktualizowany schemat bazy danych można znaleźć <a href = "https://github.com/MrResor/currency_includer/blob/main/dbschema.txt">tutaj</a>. Jest to ten sam schemat który został dostarczony jako model bazy dancyh klienta z tabelą stworzoną przy użyciu opcji "-s" skryptu. Warto jednak dodać że dostarzona nam baza dancyh nie przechowuje poprawnie cen, gdyż ignoruje wszystkie wartości po przecinku(decimal(10,0) powinno zostać zamieniona na decimal(10,2)). Dodatkowo, przy użyciu danych dostarczonych do zapełnienia tabeli, nie dało się wstawić rekordów to tabeli "sellers". Było to spowodowane regułą która wymagała litery 'B' na 3ciej kolumnie, a wszystkie dane miałt tam literę 'S'.