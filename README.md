# DeepVocab Backend

## To Install

Look at and run `install.sh`

## To Run

To run this backend
```
conda activate web
python app.py
```

To run flutter app
```
sudo javaconfig
# and choose 0, java 11
android-studio
```

To create database
send the following request to http://127.0.0.1:5000/graphql

```
mutation {
    test(key: "Koke_Cacao 's secret key", action: "add to db") {
        success
    }
}
```

and you should receive:

```
{
    "data": {
        "test": {
            "success": true
        }
    },
    "extensions": {},
    "errors": null
}
```

## To Run Test

We don't have unit tests yet.